"""
Certificate Configuration
Settings and constants for certificate generation
"""
import os
from pathlib import Path

# Certificate service configuration
CERTIFICATE_CONFIG = {
    # Template settings
    "template_download_timeout": 30,  # seconds
    "max_template_size": 50 * 1024 * 1024,  # 50MB
    "supported_template_types": ["pdf", "image"],
    "supported_image_formats": [".jpg", ".jpeg", ".png", ".tiff", ".bmp"],
    "supported_pdf_formats": [".pdf"],
    
    # PDF generation settings
    "default_page_size": (595, 842),  # A4 in points
    "max_page_size": (1200, 1600),   # Maximum allowed page size
    "default_font_size": 12,
    "min_font_size": 6,
    "max_font_size": 200,
    "default_font_family": "Arial",
    "pdf_quality": 95,
    
    # Content block settings
    "max_content_blocks": 50,
    "max_text_length": 1000,
    "max_coordinate_value": 2000,
    "default_text_color": "#000000",
    
    # File settings
    "temp_file_retention": 3600,  # 1 hour in seconds
    "max_filename_length": 200,
    "safe_filename_chars": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.",
    
    # Security settings
    "allowed_template_domains": [
        "storage.ybbfoundation.com",
        "cdn.ybbfoundation.com",
        "assets.ybbfoundation.com"
    ],
    "max_concurrent_generations": 10,
    "rate_limit_per_minute": 60,
    
    # Performance settings
    "enable_template_caching": True,
    "template_cache_size": 100,
    "template_cache_ttl": 1800,  # 30 minutes
}

# Font mappings for different platforms
FONT_MAPPINGS = {
    "reportlab": {
        "Arial": "Helvetica",
        "Arial Bold": "Helvetica-Bold",
        "Times New Roman": "Times-Roman",
        "Times New Roman Bold": "Times-Bold",
        "Courier New": "Courier",
        "Courier New Bold": "Courier-Bold"
    }
}

# Color definitions
COLOR_DEFINITIONS = {
    "black": "#000000",
    "white": "#ffffff",
    "red": "#ff0000",
    "green": "#00ff00",
    "blue": "#0000ff",
    "yellow": "#ffff00",
    "cyan": "#00ffff",
    "magenta": "#ff00ff",
    "gray": "#808080",
    "grey": "#808080",
    "darkgray": "#404040",
    "darkgrey": "#404040",
    "lightgray": "#c0c0c0",
    "lightgrey": "#c0c0c0"
}

# Default placeholder mappings and formats
PLACEHOLDER_FORMATS = {
    "date": "%B %d, %Y",  # January 01, 2024
    "date_short": "%m/%d/%Y",  # 01/01/2024
    "date_iso": "%Y-%m-%d",  # 2024-01-01
}

# Certificate validation rules
VALIDATION_RULES = {
    "participant": {
        "required_fields": ["id", "full_name"],
        "optional_fields": [
            "account_id", "birthdate", "gender", "nationality", "nationality_code",
            "education_level", "major", "institution", "occupation", "category",
            "picture_url", "instagram_account", "experiences", "achievements",
            "tshirt_size", "registration_date"
        ]
    },
    "program": {
        "required_fields": ["id", "name"],
        "optional_fields": ["theme", "start_date", "end_date"]
    },
    "award": {
        "required_fields": ["id", "title"],
        "optional_fields": ["description", "award_type", "order_number"]
    },
    "certificate_template": {
        "required_fields": ["id", "template_url", "template_type"],
        "optional_fields": ["preview_url", "issue_date", "published_at"]
    },
    "content_blocks": {
        "required_fields": ["type", "value", "x", "y"],
        "optional_fields": [
            "font_size", "font_family", "font_weight", 
            "text_align", "color"
        ]
    }
}

# Error messages
ERROR_MESSAGES = {
    "VALIDATION_ERROR": "Certificate data validation failed",
    "TEMPLATE_NOT_FOUND": "Certificate template not found or inaccessible",
    "GENERATION_FAILED": "Certificate generation failed",
    "SERVICE_UNAVAILABLE": "Certificate generation service is not available",
    "TEMPLATE_DOWNLOAD_FAILED": "Failed to download certificate template",
    "INVALID_CONTENT_BLOCKS": "Invalid content block configuration",
    "PDF_GENERATION_FAILED": "PDF generation failed",
    "FONT_NOT_FOUND": "Requested font is not available",
    "COLOR_PARSE_ERROR": "Invalid color specification",
    "COORDINATE_OUT_OF_BOUNDS": "Content block coordinates are out of bounds"
}

# Success messages
SUCCESS_MESSAGES = {
    "CERTIFICATE_GENERATED": "Certificate generated successfully",
    "TEMPLATE_VALIDATED": "Certificate template is valid and accessible",
    "CONTENT_BLOCKS_VALIDATED": "Content blocks are valid"
}

def get_certificate_config():
    """Get certificate configuration with environment overrides"""
    config = CERTIFICATE_CONFIG.copy()
    
    # Override with environment variables if present
    if os.getenv('CERTIFICATE_TEMPLATE_TIMEOUT'):
        config['template_download_timeout'] = int(os.getenv('CERTIFICATE_TEMPLATE_TIMEOUT'))
    
    if os.getenv('CERTIFICATE_MAX_TEMPLATE_SIZE'):
        config['max_template_size'] = int(os.getenv('CERTIFICATE_MAX_TEMPLATE_SIZE'))
    
    if os.getenv('CERTIFICATE_PDF_QUALITY'):
        config['pdf_quality'] = int(os.getenv('CERTIFICATE_PDF_QUALITY'))
    
    if os.getenv('CERTIFICATE_MAX_CONCURRENT'):
        config['max_concurrent_generations'] = int(os.getenv('CERTIFICATE_MAX_CONCURRENT'))
    
    if os.getenv('CERTIFICATE_RATE_LIMIT'):
        config['rate_limit_per_minute'] = int(os.getenv('CERTIFICATE_RATE_LIMIT'))
    
    return config

def validate_template_domain(template_url):
    """Validate if template URL is from allowed domain"""
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(template_url)
        domain = parsed_url.netloc.lower()
        
        # Allow localhost and development domains in debug mode
        if os.getenv('FLASK_ENV') == 'development':
            if domain.startswith('localhost') or domain.startswith('127.0.0.1'):
                return True
        
        # Check against allowed domains
        allowed_domains = CERTIFICATE_CONFIG['allowed_template_domains']
        for allowed_domain in allowed_domains:
            if domain == allowed_domain.lower() or domain.endswith(f'.{allowed_domain.lower()}'):
                return True
        
        return False
    except Exception:
        return False
