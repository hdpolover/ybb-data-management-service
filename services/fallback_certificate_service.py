"""
Fallback Certificate Service
Simple text-based certificate generation when PDF libraries are not available
"""
import base64
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger('ybb_api.fallback_certificate')

class FallbackCertificateService:
    """Simple fallback certificate service that generates text-based certificates"""
    
    def generate_certificate(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a simple text-based certificate"""
        try:
            # Extract basic information
            participant = certificate_data.get('participant', {})
            program = certificate_data.get('program', {})
            award = certificate_data.get('award', {})
            template = certificate_data.get('certificate_template', {})
            
            participant_name = participant.get('full_name', 'Unknown')
            program_name = program.get('name', 'Unknown Program')
            award_title = award.get('title', 'Certificate')
            issue_date = template.get('issue_date', datetime.now().strftime('%Y-%m-%d'))
            
            # Generate simple text certificate
            certificate_text = f"""
================================================================================
                            CERTIFICATE OF ACHIEVEMENT
================================================================================

This is to certify that

                              {participant_name}

has successfully completed all requirements for the

                              {program_name}

and is hereby awarded the

                              {award_title}

Date: {issue_date}

================================================================================
                        Youth Break the Boundaries Foundation
================================================================================

Note: This is a text-based certificate generated due to system limitations.
Please contact support for a full PDF certificate.
"""
            
            # Convert to base64 (simulating PDF)
            text_bytes = certificate_text.encode('utf-8')
            text_b64 = base64.b64encode(text_bytes).decode('utf-8')
            
            # Generate filename
            safe_name = ''.join(c for c in participant_name if c.isalnum() or c in ' -_')[:50]
            filename = f"Certificate-{safe_name.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.txt"
            
            logger.info(f"Generated fallback text certificate for {participant_name}")
            
            return {
                'success': True,
                'data': {
                    'certificate_id': f"fallback_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'participant_id': participant.get('id'),
                    'award_id': award.get('id'),
                    'file_name': filename,
                    'mime_type': 'text/plain',
                    'file_data': text_b64,
                    'file_size': len(text_bytes),
                    'generated_at': datetime.now().isoformat(),
                    'template_used': {
                        'id': 'fallback',
                        'type': 'text',
                        'version': '1.0'
                    },
                    'is_fallback': True
                },
                'message': 'Certificate generated using fallback text format (PDF libraries not available)'
            }
            
        except Exception as e:
            logger.error(f"Fallback certificate generation failed: {str(e)}")
            return {
                'success': False,
                'error': {
                    'code': 'FALLBACK_GENERATION_FAILED',
                    'message': f'Fallback certificate generation failed: {str(e)}'
                }
            }
