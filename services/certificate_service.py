"""
Certificate Generation Service
Handles certificate template processing and PDF generation
"""
import os
import io
import tempfile
import requests
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
import base64
import uuid
import logging
from pathlib import Path

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.colors import Color, HexColor
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfutils
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics
    from reportlab.lib.fonts import addMapping
except ImportError:
    pass  # Will handle in class initialization

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    pass  # Will handle in class initialization

try:
    import PyPDF2
except ImportError:
    pass  # Will handle in class initialization

logger = logging.getLogger('ybb_api.certificate_service')

class CertificateService:
    """Service for generating certificates from templates and content blocks"""
    
    def __init__(self):
        """Initialize certificate service"""
        self.temp_dir = Path("temp/certificates")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Check required dependencies and set availability
        self.dependencies_available = True
        self.missing_dependencies = []
        
        try:
            self._check_dependencies()
            logger.info("Certificate service initialized successfully with all dependencies")
        except ImportError as e:
            self.dependencies_available = False
            logger.error(f"Certificate service initialization failed: {str(e)}")
        
        # Initialize font cache
        self._font_cache = {}
        if self.dependencies_available:
            self._setup_fonts()
        else:
            logger.warning("Skipping font setup due to missing dependencies")
    
    def _check_dependencies(self):
        """Check if required dependencies are available"""
        missing_deps = []
        
        try:
            import reportlab
            logger.debug("reportlab dependency available")
        except ImportError as e:
            missing_deps.append("reportlab")
            logger.warning(f"reportlab not available: {e}")
        
        try:
            import PIL
            logger.debug("PIL (Pillow) dependency available")
        except ImportError as e:
            missing_deps.append("Pillow")
            logger.warning(f"PIL (Pillow) not available: {e}")
        
        try:
            import PyPDF2
            logger.debug("PyPDF2 dependency available")
        except ImportError as e:
            missing_deps.append("PyPDF2")
            logger.warning(f"PyPDF2 not available: {e}")
        
        if missing_deps:
            self.missing_dependencies = missing_deps
            logger.error(f"Missing required dependencies for certificate generation: {', '.join(missing_deps)}")
            raise ImportError(f"Missing required dependencies: {', '.join(missing_deps)}")
        
        logger.info("All certificate generation dependencies are available")
    
    def _setup_fonts(self):
        """Setup available fonts for PDF generation"""
        try:
            # Register standard fonts
            standard_fonts = {
                'Arial': 'Helvetica',
                'Times New Roman': 'Times-Roman',
                'Courier New': 'Courier'
            }
            
            for font_name, reportlab_name in standard_fonts.items():
                self._font_cache[font_name] = reportlab_name
            
            logger.info(f"Initialized {len(self._font_cache)} standard fonts for certificate generation")
            
        except Exception as e:
            logger.warning(f"Font setup encountered issues: {e}")
            # Use basic fallbacks
            self._font_cache = {
                'Arial': 'Helvetica',
                'Times New Roman': 'Times-Roman',
                'Courier New': 'Courier'
            }
    
    def generate_certificate(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a certificate from provided data
        
        Args:
            certificate_data: Dictionary containing all certificate data
            
        Returns:
            Dictionary with certificate generation result
        """
        # Check if dependencies are available
        if not self.dependencies_available:
            return {
                'success': False,
                'error': {
                    'code': 'SERVICE_UNAVAILABLE',
                    'message': f'Certificate generation service is not available. Missing dependencies: {", ".join(self.missing_dependencies)}',
                    'missing_dependencies': self.missing_dependencies
                }
            }
        
        try:
            request_id = str(uuid.uuid4())[:8]
            logger.info(f"CERTIFICATE_GENERATION_START | ID: {request_id}")
            
            # Validate input data
            validation_result = self._validate_certificate_data(certificate_data)
            if not validation_result['valid']:
                logger.error(f"CERTIFICATE_VALIDATION_FAILED | ID: {request_id} | Errors: {validation_result['errors']}")
                return {
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid certificate data',
                        'details': validation_result['errors']
                    }
                }
            
            # Extract data components
            participant = certificate_data['participant']
            program = certificate_data['program']
            award = certificate_data['award']
            certificate_template = certificate_data['certificate_template']
            content_blocks = certificate_data['content_blocks']
            
            logger.info(f"CERTIFICATE_DATA_EXTRACTED | ID: {request_id} | Participant: {participant['full_name']}")
            
            # Download and process template
            template_result = self._download_template(certificate_template)
            if not template_result['success']:
                logger.error(f"CERTIFICATE_TEMPLATE_FAILED | ID: {request_id} | Error: {template_result['error']}")
                return {
                    'success': False,
                    'error': {
                        'code': 'TEMPLATE_NOT_FOUND',
                        'message': 'Certificate template not found or inaccessible',
                        'template_url': certificate_template['template_url']
                    }
                }
            
            template_path = template_result['template_path']
            logger.info(f"CERTIFICATE_TEMPLATE_DOWNLOADED | ID: {request_id} | Path: {template_path}")
            
            # Process content blocks with placeholder replacement
            processed_blocks = self._process_content_blocks(
                content_blocks, participant, program, award, certificate_template
            )
            
            logger.info(f"CERTIFICATE_BLOCKS_PROCESSED | ID: {request_id} | Blocks: {len(processed_blocks)}")
            
            # Generate PDF certificate
            pdf_result = self._generate_pdf_certificate(
                template_path, processed_blocks, certificate_template['template_type']
            )
            
            if not pdf_result['success']:
                logger.error(f"CERTIFICATE_GENERATION_FAILED | ID: {request_id} | Error: {pdf_result['error']}")
                return {
                    'success': False,
                    'error': {
                        'code': 'GENERATION_FAILED',
                        'message': 'Failed to generate certificate due to internal error',
                        'request_id': request_id
                    }
                }
            
            # Generate filename
            filename = self._generate_filename(participant, award)
            
            # Encode PDF content
            pdf_content_b64 = base64.b64encode(pdf_result['pdf_content']).decode('utf-8')
            
            logger.info(f"CERTIFICATE_GENERATION_SUCCESS | ID: {request_id} | Size: {len(pdf_result['pdf_content'])} bytes")
            
            return {
                'success': True,
                'data': {
                    'certificate_id': f"cert_{request_id}",
                    'participant_id': participant['id'],
                    'award_id': award['id'],
                    'file_name': filename,
                    'mime_type': 'application/pdf',
                    'file_data': pdf_content_b64,
                    'file_size': len(pdf_result['pdf_content']),
                    'generated_at': datetime.now().isoformat(),
                    'template_used': {
                        'id': certificate_template['id'],
                        'type': certificate_template['template_type'],
                        'version': '1.0'
                    }
                },
                'message': 'Certificate generated successfully'
            }
            
        except Exception as e:
            logger.error(f"CERTIFICATE_GENERATION_EXCEPTION | Error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'GENERATION_FAILED',
                    'message': f'Certificate generation failed: {str(e)}',
                    'request_id': request_id if 'request_id' in locals() else 'unknown'
                }
            }
        finally:
            # Cleanup temporary files
            self._cleanup_temp_files()
    
    def _validate_certificate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate certificate generation data"""
        errors = {}
        
        # Required top-level keys
        required_keys = ['participant', 'program', 'award', 'certificate_template', 'content_blocks']
        for key in required_keys:
            if key not in data:
                errors[key] = [f"{key} is required"]
        
        # Validate participant data
        if 'participant' in data:
            participant = data['participant']
            if not isinstance(participant, dict):
                errors['participant'] = ['Must be an object']
            else:
                if not participant.get('id'):
                    errors['participant.id'] = ['Participant ID is required']
                if not participant.get('full_name'):
                    errors['participant.full_name'] = ['Full name is required']
        
        # Validate program data
        if 'program' in data:
            program = data['program']
            if not isinstance(program, dict):
                errors['program'] = ['Must be an object']
            else:
                if not program.get('id') or not isinstance(program['id'], int):
                    errors['program.id'] = ['Program ID must be a positive integer']
                if not program.get('name'):
                    errors['program.name'] = ['Program name is required']
        
        # Validate award data
        if 'award' in data:
            award = data['award']
            if not isinstance(award, dict):
                errors['award'] = ['Must be an object']
            else:
                if not award.get('id'):
                    errors['award.id'] = ['Award ID is required']
                if not award.get('title'):
                    errors['award.title'] = ['Award title is required']
        
        # Validate certificate template
        if 'certificate_template' in data:
            template = data['certificate_template']
            if not isinstance(template, dict):
                errors['certificate_template'] = ['Must be an object']
            else:
                if not template.get('template_url'):
                    errors['certificate_template.template_url'] = ['Template URL is required']
                if template.get('template_type') not in ['pdf', 'image']:
                    errors['certificate_template.template_type'] = ['Template type must be "pdf" or "image"']
        
        # Validate content blocks
        if 'content_blocks' in data:
            blocks = data['content_blocks']
            if not isinstance(blocks, list):
                errors['content_blocks'] = ['Must be an array']
            else:
                for i, block in enumerate(blocks):
                    if not isinstance(block, dict):
                        errors[f'content_blocks[{i}]'] = ['Must be an object']
                        continue
                    
                    if block.get('type') not in ['text', 'placeholder']:
                        errors[f'content_blocks[{i}].type'] = ['Type must be "text" or "placeholder"']
                    
                    if not block.get('value'):
                        errors[f'content_blocks[{i}].value'] = ['Value is required']
                    
                    if not isinstance(block.get('x'), int) or block.get('x') < 0:
                        errors[f'content_blocks[{i}].x'] = ['X coordinate must be a non-negative integer']
                    
                    if not isinstance(block.get('y'), int) or block.get('y') < 0:
                        errors[f'content_blocks[{i}].y'] = ['Y coordinate must be a non-negative integer']
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _download_template(self, template_info: Dict[str, Any]) -> Dict[str, Any]:
        """Download certificate template from URL"""
        try:
            template_url = template_info['template_url']
            template_type = template_info.get('template_type', 'pdf')
            
            logger.info(f"Downloading template from: {template_url}")
            
            # Download template file
            response = requests.get(template_url, timeout=30)
            response.raise_for_status()
            
            # Generate temporary file path
            file_extension = 'pdf' if template_type == 'pdf' else 'png'
            temp_filename = f"template_{uuid.uuid4().hex[:8]}.{file_extension}"
            template_path = self.temp_dir / temp_filename
            
            # Save template file
            with open(template_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Template downloaded successfully: {template_path}")
            
            return {
                'success': True,
                'template_path': str(template_path),
                'file_size': len(response.content)
            }
            
        except Exception as e:
            logger.error(f"Template download failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_content_blocks(self, blocks: List[Dict], participant: Dict, 
                              program: Dict, award: Dict, template: Dict) -> List[Dict]:
        """Process content blocks and replace placeholders"""
        try:
            # Create placeholder mappings
            placeholder_map = self._create_placeholder_map(participant, program, award, template)
            
            processed_blocks = []
            
            for block in blocks:
                processed_block = block.copy()
                
                if block['type'] == 'placeholder':
                    # Replace placeholder with actual value
                    placeholder_value = block['value']
                    if placeholder_value in placeholder_map:
                        processed_block['value'] = placeholder_map[placeholder_value]
                        logger.debug(f"Replaced placeholder {placeholder_value} with {processed_block['value']}")
                    else:
                        # Keep original value if no mapping found
                        logger.warning(f"No mapping found for placeholder: {placeholder_value}")
                        processed_block['value'] = placeholder_value.replace('{{', '').replace('}}', '')
                
                processed_blocks.append(processed_block)
            
            return processed_blocks
            
        except Exception as e:
            logger.error(f"Content block processing failed: {str(e)}")
            return blocks  # Return original blocks as fallback
    
    def _create_placeholder_map(self, participant: Dict, program: Dict, 
                               award: Dict, template: Dict) -> Dict[str, str]:
        """Create mapping of placeholders to actual values"""
        # Format dates
        def format_date(date_value):
            if not date_value:
                return ""
            
            if isinstance(date_value, str):
                try:
                    # Try parsing common date formats
                    for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                        try:
                            parsed_date = datetime.strptime(date_value, fmt)
                            return parsed_date.strftime('%B %d, %Y')
                        except ValueError:
                            continue
                    return date_value
                except:
                    return date_value
            elif isinstance(date_value, (datetime, date)):
                return date_value.strftime('%B %d, %Y')
            else:
                return str(date_value)
        
        # Create comprehensive mapping
        mapping = {
            '{{participant_name}}': participant.get('full_name', ''),
            '{{award_title}}': award.get('title', ''),
            '{{program_name}}': program.get('name', ''),
            '{{program_theme}}': program.get('theme', ''),
            '{{date}}': format_date(template.get('issue_date')),
            '{{participant_institution}}': participant.get('institution', ''),
            '{{participant_category}}': participant.get('category', ''),
            '{{participant_nationality}}': participant.get('nationality', ''),
            '{{participant_education_level}}': participant.get('education_level', ''),
            '{{participant_major}}': participant.get('major', ''),
            '{{participant_occupation}}': participant.get('occupation', ''),
            '{{award_description}}': award.get('description', ''),
            '{{award_type}}': award.get('award_type', ''),
        }
        
        # Add program date ranges
        if program.get('start_date') and program.get('end_date'):
            start_date = format_date(program['start_date'])
            end_date = format_date(program['end_date'])
            mapping['{{program_dates}}'] = f"{start_date} to {end_date}"
        
        return mapping
    
    def _generate_pdf_certificate(self, template_path: str, content_blocks: List[Dict], 
                                 template_type: str) -> Dict[str, Any]:
        """Generate PDF certificate with content blocks overlaid on template"""
        try:
            pdf_buffer = io.BytesIO()
            
            if template_type == 'pdf':
                # Handle PDF template
                result = self._generate_from_pdf_template(template_path, content_blocks, pdf_buffer)
            else:
                # Handle image template
                result = self._generate_from_image_template(template_path, content_blocks, pdf_buffer)
            
            if result['success']:
                pdf_content = pdf_buffer.getvalue()
                pdf_buffer.close()
                
                return {
                    'success': True,
                    'pdf_content': pdf_content
                }
            else:
                pdf_buffer.close()
                return result
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_from_pdf_template(self, template_path: str, content_blocks: List[Dict], 
                                   output_buffer: io.BytesIO) -> Dict[str, Any]:
        """Generate certificate from PDF template"""
        try:
            # Read the original PDF
            with open(template_path, 'rb') as template_file:
                template_pdf = PyPDF2.PdfReader(template_file)
                
                if len(template_pdf.pages) == 0:
                    raise ValueError("Template PDF has no pages")
                
                # Get first page (assuming single-page certificate)
                template_page = template_pdf.pages[0]
                page_width = float(template_page.mediabox.width)
                page_height = float(template_page.mediabox.height)
                
                # Create overlay with content blocks
                overlay_buffer = io.BytesIO()
                overlay_canvas = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))
                
                # Add content blocks to overlay
                for block in content_blocks:
                    self._add_content_block_to_canvas(overlay_canvas, block, page_height)
                
                overlay_canvas.save()
                overlay_buffer.seek(0)
                
                # Create overlay PDF reader
                overlay_pdf = PyPDF2.PdfReader(overlay_buffer)
                overlay_page = overlay_pdf.pages[0]
                
                # Merge template and overlay
                template_page.merge_page(overlay_page)
                
                # Write final PDF
                writer = PyPDF2.PdfWriter()
                writer.add_page(template_page)
                writer.write(output_buffer)
                
                overlay_buffer.close()
                
                return {'success': True}
                
        except Exception as e:
            logger.error(f"PDF template processing failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_from_image_template(self, template_path: str, content_blocks: List[Dict], 
                                     output_buffer: io.BytesIO) -> Dict[str, Any]:
        """Generate certificate from image template"""
        try:
            # Open image template
            with Image.open(template_path) as template_image:
                # Convert to RGB if necessary
                if template_image.mode != 'RGB':
                    template_image = template_image.convert('RGB')
                
                # Create PDF with image as background
                page_width, page_height = template_image.size
                
                # Scale to fit standard page size if too large
                max_width, max_height = 595, 842  # A4 size in points
                if page_width > max_width or page_height > max_height:
                    scale = min(max_width / page_width, max_height / page_height)
                    page_width = int(page_width * scale)
                    page_height = int(page_height * scale)
                    template_image = template_image.resize((page_width, page_height), Image.Resampling.LANCZOS)
                
                # Create PDF canvas
                pdf_canvas = canvas.Canvas(output_buffer, pagesize=(page_width, page_height))
                
                # Add background image
                img_buffer = io.BytesIO()
                template_image.save(img_buffer, format='JPEG', quality=95)
                img_buffer.seek(0)
                
                pdf_canvas.drawImage(ImageReader(img_buffer), 0, 0, page_width, page_height)
                
                # Add content blocks
                for block in content_blocks:
                    self._add_content_block_to_canvas(pdf_canvas, block, page_height)
                
                pdf_canvas.save()
                img_buffer.close()
                
                return {'success': True}
                
        except Exception as e:
            logger.error(f"Image template processing failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _add_content_block_to_canvas(self, canvas_obj: canvas.Canvas, block: Dict, page_height: float):
        """Add a content block to the PDF canvas"""
        try:
            # Extract block properties
            text = str(block.get('value', ''))
            x = float(block.get('x', 0))
            y = float(page_height) - float(block.get('y', 0))  # PDF coordinates are bottom-up
            font_size = int(block.get('font_size', 12))
            font_family = block.get('font_family', 'Arial')
            font_weight = block.get('font_weight', 'normal')
            text_align = block.get('text_align', 'left')
            color = block.get('color', '#000000')
            
            # Map font family to ReportLab font
            font_name = self._get_reportlab_font(font_family, font_weight)
            
            # Set font and color
            canvas_obj.setFont(font_name, font_size)
            canvas_obj.setFillColor(self._parse_color(color))
            
            # Handle text alignment
            if text_align == 'center':
                text_width = canvas_obj.stringWidth(text, font_name, font_size)
                x = x - (text_width / 2)
            elif text_align == 'right':
                text_width = canvas_obj.stringWidth(text, font_name, font_size)
                x = x - text_width
            
            # Draw text
            canvas_obj.drawString(x, y, text)
            
        except Exception as e:
            logger.warning(f"Failed to add content block: {str(e)}")
            # Continue processing other blocks
    
    def _get_reportlab_font(self, font_family: str, font_weight: str) -> str:
        """Get ReportLab font name from font family and weight"""
        # Map common font families
        font_map = {
            'Arial': 'Helvetica',
            'Times New Roman': 'Times-Roman',
            'Courier New': 'Courier'
        }
        
        base_font = font_map.get(font_family, 'Helvetica')
        
        # Handle font weights
        if font_weight in ['bold', 'bolder', '600', '700', '800', '900']:
            if base_font == 'Helvetica':
                return 'Helvetica-Bold'
            elif base_font == 'Times-Roman':
                return 'Times-Bold'
            elif base_font == 'Courier':
                return 'Courier-Bold'
        
        return base_font
    
    def _parse_color(self, color_str: str) -> Color:
        """Parse color string to ReportLab Color object"""
        try:
            if color_str.startswith('#'):
                return HexColor(color_str)
            else:
                # Handle named colors
                color_map = {
                    'black': HexColor('#000000'),
                    'white': HexColor('#ffffff'),
                    'red': HexColor('#ff0000'),
                    'green': HexColor('#00ff00'),
                    'blue': HexColor('#0000ff'),
                    'gray': HexColor('#808080'),
                    'grey': HexColor('#808080')
                }
                return color_map.get(color_str.lower(), HexColor('#000000'))
        except:
            return HexColor('#000000')  # Default to black
    
    def _generate_filename(self, participant: Dict, award: Dict) -> str:
        """Generate certificate filename"""
        try:
            participant_name = participant.get('full_name', 'Unknown').replace(' ', '-')
            award_title = award.get('title', 'Certificate').replace(' ', '-')
            date_str = datetime.now().strftime('%Y%m%d')
            
            # Clean filename
            safe_name = ''.join(c for c in participant_name if c.isalnum() or c in '-_')[:50]
            safe_award = ''.join(c for c in award_title if c.isalnum() or c in '-_')[:30]
            
            return f"Certificate-{safe_name}-{safe_award}-{date_str}.pdf"
            
        except Exception as e:
            logger.warning(f"Filename generation failed: {e}")
            return f"Certificate-{datetime.now().strftime('%Y%m%d')}.pdf"
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            if self.temp_dir.exists():
                # Remove files older than 1 hour
                import time
                current_time = time.time()
                for file_path in self.temp_dir.glob('*'):
                    if file_path.is_file():
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > 3600:  # 1 hour
                            file_path.unlink()
                            logger.debug(f"Cleaned up old temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Temp file cleanup failed: {e}")
