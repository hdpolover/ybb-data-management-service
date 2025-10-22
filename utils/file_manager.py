"""
Export File Manager - Handles filename generation and sanitization
for YBB export service with enhanced naming functionality
"""
import os
import re
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ExportFileManager:
    """
    Manages file naming, sanitization, and storage for export operations
    """
    
    def __init__(self, base_storage_path=None):
        # Use project-specific temp directory instead of Docker path
        if base_storage_path is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            base_storage_path = os.path.join(project_root, "temp", "exports")
        self.base_storage_path = base_storage_path
        self.max_filename_length = 200
        self.excel_sheet_name_max_length = 31
        
    def generate_filename(self, request_data, export_id, batch_info=None):
        """
        Generate appropriate filename based on request data
        
        Args:
            request_data (dict): The export request payload
            export_id (str): Unique export identifier
            batch_info (dict): Batch information for multi-file exports
                               Format: {'number': 1, 'total': 3, 'batch': 1}
            
        Returns:
            str: Generated filename
        """
        try:
            # Use provided filename if available
            if 'filename' in request_data and request_data['filename']:
                base_filename = request_data['filename']
                
                # Handle batch files
                if batch_info:
                    # Remove .xlsx extension and add batch info
                    base_name = base_filename.replace('.xlsx', '').replace('.csv', '')
                    batch_number = batch_info.get('number', batch_info.get('batch', 1))
                    total_batches = batch_info.get('total', 1)
                    batch_suffix = f"_batch_{batch_number}_of_{total_batches}"
                    
                    # Determine file extension
                    original_ext = '.xlsx' if '.xlsx' in base_filename else '.csv'
                    return f"{base_name}{batch_suffix}{original_ext}"
                
                return base_filename
            
            # Fallback to existing naming convention
            export_type = request_data.get('export_type', 'export')
            template = request_data.get('template', 'standard')
            date_str = datetime.now().strftime('%d-%m-%Y')
            time_str = datetime.now().strftime('%H%M%S')
            
            if batch_info:
                batch_number = batch_info.get('number', batch_info.get('batch', 1))
                return f"{export_type}_{template}_{export_id}_batch_{batch_number}_{date_str}_{time_str}.xlsx"
            
            return f"{export_type}_{template}_{export_id}_{date_str}_{time_str}.xlsx"
            
        except Exception as e:
            logger.error(f"Error generating filename: {str(e)}")
            # Ultimate fallback
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return f"export_{export_id}_{timestamp}.xlsx"
    
    def generate_zip_filename(self, request_data, export_id):
        """
        Generate ZIP archive filename
        
        Args:
            request_data (dict): The export request payload
            export_id (str): Unique export identifier
            
        Returns:
            str: ZIP filename
        """
        try:
            if 'filename' in request_data and request_data['filename']:
                base_filename = request_data['filename'].replace('.xlsx', '').replace('.csv', '')
                return f"{base_filename}_complete_export.zip"
            
            export_type = request_data.get('export_type', 'export')
            template = request_data.get('template', 'standard')
            date_str = datetime.now().strftime('%d-%m-%Y')
            return f"{export_type}_{template}_{export_id}_complete_{date_str}.zip"
            
        except Exception as e:
            logger.error(f"Error generating ZIP filename: {str(e)}")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return f"export_{export_id}_complete_{timestamp}.zip"
    
    def get_sheet_name(self, request_data, batch_info=None):
        """
        Get Excel sheet name from request or generate default
        
        Args:
            request_data (dict): The export request payload
            batch_info (dict): Batch information for multi-file exports
            
        Returns:
            str: Sheet name for Excel file (max 31 characters)
        """
        try:
            # Use provided sheet name if available
            if 'sheet_name' in request_data and request_data['sheet_name']:
                sheet_name = request_data['sheet_name']
                
                # Add batch info if needed
                if batch_info:
                    batch_number = batch_info.get('number', batch_info.get('batch', 1))
                    sheet_name = f"{sheet_name} (Batch {batch_number})"
                
                # Truncate to Excel limit
                return sheet_name[:self.excel_sheet_name_max_length]
            
            # Generate default sheet name
            export_type = request_data.get('export_type', 'Data')
            date_str = datetime.now().strftime('%b %Y')
            
            if batch_info:
                batch_number = batch_info.get('number', batch_info.get('batch', 1))
                sheet_name = f"{export_type.title()} {date_str} (Batch {batch_number})"
            else:
                sheet_name = f"{export_type.title()} {date_str}"
            
            # Truncate to Excel limit
            return sheet_name[:self.excel_sheet_name_max_length]
            
        except Exception as e:
            logger.error(f"Error generating sheet name: {str(e)}")
            return "Export Data"
    
    def sanitize_filename(self, filename):
        """
        Sanitize filename to ensure it's safe for filesystem
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Sanitized filename
        """
        if not filename:
            return "export.xlsx"
        
        try:
            # Remove or replace invalid characters for Windows/Unix filesystems
            sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            # Remove control characters
            sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
            
            # Replace multiple underscores with single underscore
            sanitized = re.sub(r'_+', '_', sanitized)
            
            # Remove leading/trailing whitespace and dots
            sanitized = sanitized.strip(' .')
            
            # Ensure filename is not empty after sanitization
            if not sanitized:
                sanitized = "export"
            
            # Handle file extension
            name, ext = os.path.splitext(sanitized)
            if not ext:
                ext = '.xlsx'  # Default extension
            
            # Limit length to prevent filesystem issues
            if len(sanitized) > self.max_filename_length:
                max_name_length = self.max_filename_length - len(ext)
                sanitized = name[:max_name_length] + ext
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Error sanitizing filename '{filename}': {str(e)}")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return f"export_{timestamp}.xlsx"
    
    def get_safe_storage_path(self, filename):
        """
        Get safe storage path for the file
        
        Args:
            filename (str): The filename
            
        Returns:
            str: Full path to store the file
        """
        try:
            # Ensure base storage path exists
            Path(self.base_storage_path).mkdir(parents=True, exist_ok=True)
            
            # Sanitize filename
            safe_filename = self.sanitize_filename(filename)
            
            # Combine path
            full_path = os.path.join(self.base_storage_path, safe_filename)
            
            return full_path
            
        except Exception as e:
            logger.error(f"Error creating storage path: {str(e)}")
            # Fallback to temp directory
            import tempfile
            temp_dir = tempfile.gettempdir()
            safe_filename = self.sanitize_filename(filename)
            return os.path.join(temp_dir, safe_filename)
    
    def calculate_compression_ratio(self, original_files, zip_path):
        """
        Calculate compression ratio for ZIP archive
        
        Args:
            original_files (list): List of original file paths or sizes
            zip_path (str): Path to ZIP file
            
        Returns:
            str: Compression ratio as percentage string
        """
        try:
            # Calculate total original size
            total_original_size = 0
            for file_info in original_files:
                if isinstance(file_info, dict) and 'file_size' in file_info:
                    total_original_size += file_info['file_size']
                elif isinstance(file_info, str) and os.path.exists(file_info):
                    total_original_size += os.path.getsize(file_info)
                elif isinstance(file_info, (int, float)):
                    total_original_size += file_info
            
            # Get compressed size
            if os.path.exists(zip_path):
                compressed_size = os.path.getsize(zip_path)
            else:
                return "0.0"
            
            # Calculate ratio
            if total_original_size > 0:
                ratio = ((total_original_size - compressed_size) / total_original_size) * 100
                return f"{ratio:.1f}"
            
            return "0.0"
            
        except Exception as e:
            logger.error(f"Error calculating compression ratio: {str(e)}")
            return "0.0"
    
    def validate_filename_params(self, request_data):
        """
        Validate filename-related parameters in request
        
        Args:
            request_data (dict): Request data to validate
            
        Returns:
            dict: Validation result with 'valid' boolean and 'message'
        """
        try:
            # Check filename if provided
            if 'filename' in request_data:
                filename = request_data['filename']
                
                if not isinstance(filename, str):
                    return {
                        'valid': False,
                        'message': 'Filename must be a string'
                    }
                
                if len(filename.strip()) == 0:
                    return {
                        'valid': False,
                        'message': 'Filename cannot be empty'
                    }
                
                # Check for obviously malicious patterns
                dangerous_patterns = ['../', '..\\', '/etc/', 'C:\\', 'cmd.exe', 'powershell']
                filename_lower = filename.lower()
                for pattern in dangerous_patterns:
                    if pattern.lower() in filename_lower:
                        return {
                            'valid': False,
                            'message': f'Filename contains potentially dangerous pattern: {pattern}'
                        }
            
            # Check sheet name if provided
            if 'sheet_name' in request_data:
                sheet_name = request_data['sheet_name']
                
                if not isinstance(sheet_name, str):
                    return {
                        'valid': False,
                        'message': 'Sheet name must be a string'
                    }
                
                # Excel sheet name restrictions (cannot contain: \ / ? * [ ] : )
                invalid_chars = ['\\', '/', '?', '*', '[', ']', ':']
                for char in invalid_chars:
                    if char in sheet_name:
                        return {
                            'valid': False,
                            'message': f'Sheet name cannot contain character: {char}'
                        }
            
            return {'valid': True, 'message': 'Valid'}
            
        except Exception as e:
            logger.error(f"Error validating filename params: {str(e)}")
            return {
                'valid': False,
                'message': f'Validation error: {str(e)}'
            }
    
    def cleanup_temp_files(self, file_paths):
        """
        Clean up temporary files
        
        Args:
            file_paths (list): List of file paths to clean up
        """
        cleaned_count = 0
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned_count += 1
                    logger.debug(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {file_path}: {str(e)}")
        
        logger.info(f"Cleaned up {cleaned_count} temporary files")
        return cleaned_count
