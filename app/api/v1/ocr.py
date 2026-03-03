# -*- coding: utf-8 -*-
"""
OCR API Blueprint - Endpoints for OCR operations.
"""
from flask import Blueprint, request, send_file
from app.core.response import APIResponse
from app.core.middleware import validate_file_upload, handle_exceptions
from app.processors import OCRProcessor

ocr_bp = Blueprint('ocr', __name__)

# Initialize processor
processor = OCRProcessor()


@ocr_bp.route('/check', methods=['GET'])
def check_tesseract():
    """
    Check if Tesseract OCR is installed and configured.
    
    Returns:
        JSON with installation status
    """
    return APIResponse.success(processor.check_tesseract())


@ocr_bp.route('/languages', methods=['GET'])
def get_languages():
    """
    Get available OCR languages.
    
    Returns:
        JSON with available languages
    """
    return APIResponse.success(processor.get_available_languages())


@ocr_bp.route('/preview', methods=['POST'])
@handle_exceptions
@validate_file_upload(allowed_extensions=['.pdf'], max_size_mb=50)
def ocr_preview():
    """
    Generate preview of PDF for OCR.
    
    Form data:
        file: PDF file
    
    Returns:
        JSON with base64 preview image and page count
    """
    file = request.files['file']
    content = file.read()
    
    preview = processor.get_preview(content, page_number=0, zoom=0.4)
    pages = processor.get_page_count(content)
    
    return APIResponse.success({
        'preview': preview,
        'pages': pages
    })


@ocr_bp.route('/extract', methods=['POST'])
@handle_exceptions
@validate_file_upload(allowed_extensions=['.pdf'], max_size_mb=50)
def ocr_extract():
    """
    Extract text from PDF using OCR.
    
    Form data:
        file: PDF file
        language: OCR language (default: por)
        dpi: Resolution (default: 300)
    
    Returns:
        JSON with extracted text
    """
    file = request.files['file']
    lang = request.form.get('language', 'por')
    dpi = int(request.form.get('dpi', 300))
    
    result = processor.extract_text(file, {
        'language': lang,
        'dpi': dpi
    })
    
    return APIResponse.success(result)


@ocr_bp.route('/convert', methods=['POST'])
@handle_exceptions
@validate_file_upload(allowed_extensions=['.pdf'], max_size_mb=50)
def ocr_convert():
    """
    Convert PDF using OCR to different format.
    
    Form data:
        file: PDF file
        language: OCR language (default: por)
        dpi: Resolution (default: 300)
        output_format: 'txt', 'docx', or 'pdf' (default: txt)
    
    Returns:
        Converted file as download
    """
    file = request.files['file']
    lang = request.form.get('language', 'por')
    dpi = int(request.form.get('dpi', 300))
    output_format = request.form.get('output_format', 'txt')
    
    result = processor.process(file, {
        'language': lang,
        'dpi': dpi,
        'output_format': output_format
    })
    
    if not result.success:
        return APIResponse.error(result.error, 'OCR_ERROR')
    
    return send_file(
        result.output,
        as_attachment=True,
        download_name=result.filename,
        mimetype=result.mimetype
    )


@ocr_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """
    Get supported formats for OCR.
    
    Returns:
        JSON with supported formats and output options
    """
    return APIResponse.success({
        'input_formats': processor.get_supported_formats(),
        'output_formats': ['txt', 'docx', 'pdf'],
        'description': processor.description
    })
