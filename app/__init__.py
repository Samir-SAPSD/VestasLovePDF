# -*- coding: utf-8 -*-
"""
Application Factory Pattern.
Creates and configures the Flask application.
"""
from flask import Flask
from flask_cors import CORS


def create_app(config_name: str = 'default') -> Flask:
    """
    Application factory function.
    
    Args:
        config_name: Configuration name ('default', 'development', 'production', 'testing')
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(get_config(config_name))
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def get_config(config_name: str):
    """Get configuration class based on name."""
    configs = {
        'default': 'app.config.Config',
        'development': 'app.config.DevelopmentConfig',
        'production': 'app.config.ProductionConfig',
        'testing': 'app.config.TestingConfig'
    }
    return configs.get(config_name, configs['default'])


def init_extensions(app: Flask):
    """Initialize Flask extensions."""
    # Enable CORS for API endpoints
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })


def register_blueprints(app: Flask):
    """Register all blueprints."""
    # Import and register API v1
    from app.api.v1 import api_v1
    app.register_blueprint(api_v1, url_prefix='/api/v1')
    
    # Import and register pages blueprint (for template rendering)
    from app.pages import pages_bp
    app.register_blueprint(pages_bp)


def register_error_handlers(app: Flask):
    """Register global error handlers."""
    from app.core.response import APIResponse
    from app.core.exceptions import AppException
    
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        return APIResponse.error(error.message, error.code, error.status)
    
    @app.errorhandler(404)
    def handle_not_found(error):
        # Check if it's an API request
        from flask import request
        if request.path.startswith('/api/'):
            return APIResponse.error('Endpoint não encontrado', 'NOT_FOUND', 404)
        # For non-API requests, return default 404
        return 'Página não encontrada', 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        from flask import request
        if request.path.startswith('/api/'):
            return APIResponse.error('Erro interno do servidor', 'INTERNAL_ERROR', 500)
        return 'Erro interno do servidor', 500
