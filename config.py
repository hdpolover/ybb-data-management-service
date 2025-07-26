"""
Configuration file for the YBB Data Management Service
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ybb-data-service-secret-key-2024')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # API settings
    API_HOST = os.environ.get('API_HOST', '0.0.0.0')
    API_PORT = int(os.environ.get('PORT') or os.environ.get('API_PORT', 5000))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 104857600))  # 100MB
    
    # Performance settings
    MAX_CHUNK_SIZE = int(os.environ.get('MAX_CHUNK_SIZE', 1000))
    MAX_MEMORY_MB = int(os.environ.get('MAX_MEMORY_MB', 500))
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 300))  # 5 minutes
    
    # File settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'temp')
    EXPORT_RETENTION_HOURS = int(os.environ.get('EXPORT_RETENTION_HOURS', 24))
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/ybb_api.log')
    ACCESS_LOG = os.environ.get('ACCESS_LOG', 'logs/ybb_api_access.log')
    LOG_RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS', 7))
    LOG_MAX_SIZE_MB = int(os.environ.get('LOG_MAX_SIZE_MB', 10))
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Rate limiting (requests per minute per IP)
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 60))
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 30))  # seconds

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    API_HOST = '127.0.0.1'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # Enhanced security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance optimizations
    MAX_CHUNK_SIZE = 500  # Smaller chunks in production
    REQUEST_TIMEOUT = 180  # Shorter timeout

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB for testing

# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, DevelopmentConfig)
