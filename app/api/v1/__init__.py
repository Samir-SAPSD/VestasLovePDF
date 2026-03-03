# -*- coding: utf-8 -*-
"""
API v1 module - Blueprint registration.
"""
from flask import Blueprint

# Create main API v1 blueprint
api_v1 = Blueprint('api_v1', __name__)

# Import and register sub-blueprints
from app.api.v1.compressor import compressor_bp
from app.api.v1.converter import converter_bp
from app.api.v1.pdf_tools import pdf_tools_bp
from app.api.v1.ocr import ocr_bp

# Register blueprints with prefixes
api_v1.register_blueprint(compressor_bp, url_prefix='/compress')
api_v1.register_blueprint(converter_bp, url_prefix='/convert')
api_v1.register_blueprint(pdf_tools_bp, url_prefix='/pdf')
api_v1.register_blueprint(ocr_bp, url_prefix='/ocr')


@api_v1.route('/health')
def health_check():
    """API health check endpoint."""
    from app.core.response import APIResponse
    return APIResponse.success({
        'status': 'healthy',
        'version': 'v1'
    })


@api_v1.route('/processors')
def list_processors():
    """List all available processors."""
    from app.core.response import APIResponse
    from app.processors.base import ProcessorRegistry
    return APIResponse.success(ProcessorRegistry.list_all())
