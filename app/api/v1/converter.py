# -*- coding: utf-8 -*-
"""
Converter API Blueprint - Endpoints for file conversion.
"""
from flask import Blueprint, request, send_file
from app.core.response import APIResponse
from app.core.middleware import validate_file_upload, handle_exceptions
from app.processors import ConverterProcessor, ExcelConverterProcessor

converter_bp = Blueprint('converter', __name__)

# Initialize processors
converter = ConverterProcessor()
excel_converter = ExcelConverterProcessor()


@converter_bp.route('/', methods=['POST'])
@handle_exceptions
@validate_file_upload(max_size_mb=100)
def convert_file():
    """
    Convert file to different format.
    
    Form data:
        file: File to convert
        conv_type: Conversion type (e.g., 'img_to_pdf', 'pdf_to_jpg', 'excel_to_csv')
    
    Returns:
        Converted file as download
    """
    file = request.files['file']
    conv_type = request.form.get('conv_type')
    
    if not conv_type:
        return APIResponse.error('Tipo de conversão não especificado', 'MISSING_CONV_TYPE')
    
    result = converter.process(file, {'conv_type': conv_type})
    
    if not result.success:
        return APIResponse.error(result.error, 'CONVERSION_ERROR')
    
    return send_file(
        result.output,
        as_attachment=True,
        download_name=result.filename,
        mimetype=result.mimetype
    )


@converter_bp.route('/detect', methods=['POST'])
@handle_exceptions
@validate_file_upload(max_size_mb=100)
def detect_format():
    """
    Detect file format and return available conversions.
    
    Form data:
        file: File to analyze
    
    Returns:
        JSON with format info and available conversions
    """
    file = request.files['file']
    
    result = converter.detect_format(file.filename)
    
    if result:
        return APIResponse.success(result)
    else:
        return APIResponse.error('Formato de arquivo não reconhecido', 'UNKNOWN_FORMAT')


@converter_bp.route('/excel/detect', methods=['POST'])
@handle_exceptions
@validate_file_upload(
    allowed_extensions=['.xlsx', '.xls', '.xlsb', '.ods'],
    max_size_mb=100
)
def detect_excel():
    """
    Detect Excel file version and return available conversions.
    
    Form data:
        file: Excel file to analyze
    
    Returns:
        JSON with Excel format info and available conversions
    """
    file = request.files['file']
    
    result = excel_converter.get_conversions_for_file(file.filename)
    
    if result:
        return APIResponse.success(result)
    else:
        return APIResponse.error('Formato de arquivo não reconhecido', 'UNKNOWN_FORMAT')


@converter_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """
    Get list of supported formats for conversion.
    
    Returns:
        JSON with supported formats
    """
    return APIResponse.success({
        'formats': converter.get_supported_formats(),
        'description': converter.description
    })
