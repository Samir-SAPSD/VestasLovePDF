# -*- coding: utf-8 -*-
"""
Compressor API Blueprint - Endpoints for file compression.
"""
from flask import Blueprint, request, send_file
from app.core.response import APIResponse
from app.core.middleware import validate_file_upload, handle_exceptions
from app.processors import CompressorProcessor

compressor_bp = Blueprint('compressor', __name__)

# Initialize processor
processor = CompressorProcessor()


@compressor_bp.route('/', methods=['POST'])
@handle_exceptions
@validate_file_upload(max_size_mb=100)
def compress_file():
    """
    Compress a file (image, PDF, or any file to ZIP).
    
    Form data:
        file: File to compress
        compression_type: 'auto', 'image', 'pdf', 'zip' (default: auto)
        quality: 1-100 (default: 85)
    
    Returns:
        Compressed file as download
    """
    file = request.files['file']
    compression_type = request.form.get('compression_type', 'auto')
    quality = int(request.form.get('quality', 85))
    
    result = processor.process(file, {
        'compression_type': compression_type,
        'quality': quality
    })
    
    if not result.success:
        return APIResponse.error(result.error, 'COMPRESSION_ERROR')
    
    return send_file(
        result.output,
        as_attachment=True,
        download_name=result.filename,
        mimetype=result.mimetype
    )


@compressor_bp.route('/estimate', methods=['POST'])
@handle_exceptions
@validate_file_upload(max_size_mb=100)
def estimate_compression():
    """
    Estimate compression result without compressing.
    
    Form data:
        file: File to analyze
        compression_type: 'auto', 'image', 'pdf', 'zip' (default: auto)
        quality: 1-100 (default: 85)
    
    Returns:
        JSON with estimated sizes and compression ratio
    """
    file = request.files['file']
    compression_type = request.form.get('compression_type', 'auto')
    quality = int(request.form.get('quality', 85))
    
    result = processor.estimate(file, {
        'compression_type': compression_type,
        'quality': quality
    })
    
    return APIResponse.success(result)


@compressor_bp.route('/target-quality', methods=['POST'])
@handle_exceptions
@validate_file_upload(max_size_mb=100)
def calculate_target_quality():
    """
    Calculate quality needed to achieve target file size.
    
    Form data:
        file: File to analyze
        target_size: Target size (numeric)
        target_unit: 'KB' or 'MB' (default: KB)
        compression_type: 'auto', 'image', 'pdf', 'zip' (default: auto)
    
    Returns:
        JSON with recommended quality setting
    """
    file = request.files['file']
    target_size = float(request.form.get('target_size', 0))
    target_unit = request.form.get('target_unit', 'KB')
    compression_type = request.form.get('compression_type', 'auto')
    
    # Convert to bytes
    if target_unit == 'KB':
        target_size_bytes = int(target_size * 1024)
    elif target_unit == 'MB':
        target_size_bytes = int(target_size * 1024 * 1024)
    else:
        target_size_bytes = int(target_size)
    
    result = processor.calculate_quality_for_target(file, target_size_bytes, compression_type)
    
    return APIResponse.success(result)


@compressor_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """
    Get list of supported formats for compression.
    
    Returns:
        JSON with supported formats
    """
    return APIResponse.success({
        'formats': processor.get_supported_formats(),
        'description': processor.description
    })
