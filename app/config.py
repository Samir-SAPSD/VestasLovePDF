# -*- coding: utf-8 -*-
"""
Application configuration.
"""
import os


class Config:
    """Base configuration."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB max file size
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    
    # Debug mode
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    
    # More permissive CORS in development
    CORS_ORIGINS = ['*']


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    
    # Stricter settings in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Production CORS origins should be set via environment variable
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
