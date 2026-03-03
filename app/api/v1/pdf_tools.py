# -*- coding: utf-8 -*-
"""
PDF Tools API Blueprint - Endpoints for PDF operations (merge, split).
"""
from flask import Blueprint, request, send_file
from app.core.response import APIResponse
from app.core.middleware import validate_file_upload, validate_json_body, handle_exceptions
from app.processors import PDFMergerProcessor, PDFSplitterProcessor

pdf_tools_bp = Blueprint('pdf_tools', __name__)

# Initialize processors
merger = PDFMergerProcessor()
splitter = PDFSplitterProcessor()


# ==================== MERGER ENDPOINTS ====================

@pdf_tools_bp.route('/merge/preview', methods=['POST'])
@handle_exceptions
@validate_file_upload(allowed_extensions=['.pdf'], max_size_mb=50)
def pdf_preview():
    """
    Generate preview of first page of PDF.
    
    Form data:
        file: PDF file
    
    Returns:
        JSON with base64 preview image and page count
    """
    file = request.files['file']
    content = file.read()
    
    preview = merger.get_preview(content, page_number=0, zoom=0.5)
    pages = merger.get_page_count(content)
    
    return APIResponse.success({
        'preview': preview,
        'pages': pages
    })


@pdf_tools_bp.route('/merge', methods=['POST'])
@handle_exceptions
@validate_json_body(required_fields=['files'])
def pdf_merge():
    """
    Merge multiple PDFs into one.
    
    JSON body:
        files: Array of objects with:
            - content: Base64 encoded PDF
            - rotation: Rotation angle (0, 90, 180, 270)
    
    Returns:
        Merged PDF file as download
    """
    data = request.get_json()
    files = data.get('files', [])
    
    result = merger.process(None, {'files': files})
    
    if not result.success:
        return APIResponse.error(result.error, 'MERGE_ERROR')
    
    return send_file(
        result.output,
        as_attachment=True,
        download_name=result.filename,
        mimetype=result.mimetype
    )


# ==================== SPLITTER ENDPOINTS ====================

@pdf_tools_bp.route('/split/load', methods=['POST'])
@handle_exceptions
@validate_file_upload(allowed_extensions=['.pdf'], max_size_mb=50)
def pdf_splitter_load():
    """
    Load all pages of PDF for preview/split.
    
    Form data:
        file: PDF file
    
    Returns:
        JSON with previews array and page count
    """
    file = request.files['file']
    content = file.read()
    
    previews = splitter.get_all_previews(content, zoom=0.4)
    pages = splitter.get_page_count(content)
    
    return APIResponse.success({
        'previews': previews,
        'pages': pages
    })


@pdf_tools_bp.route('/split', methods=['POST'])
@handle_exceptions
@validate_json_body(required_fields=['content'])
def pdf_split():
    """
    Split PDF with multiple modes.
    
    JSON body:
        content: Base64 encoded PDF
        mode: 'select', 'markers', or 'range'
        splitPoints: Array of pages (mode=select) or split points (mode=markers)
        pagesPerFile: Number of pages per file (mode=range)
        pageRange: Custom range string like "1-3, 5, 7-10" (mode=range)
        fileName: Original filename (optional)
    
    Returns:
        ZIP file with split PDFs or single PDF as download
    """
    data = request.get_json()
    mode = data.get('mode', 'markers')
    content = data.get('content', '')
    split_points = data.get('splitPoints', [])
    pages_per_file = data.get('pagesPerFile')
    page_range = data.get('pageRange', '')
    filename = data.get('fileName', 'documento')
    
    # Process based on mode
    if mode == 'select':
        # Extract only selected pages into a single PDF
        result = splitter.process(None, {
            'content': content,
            'mode': 'select',
            'selected_pages': split_points,
            'filename': filename
        })
    elif mode == 'range':
        # Split by range or pages per file
        result = splitter.process(None, {
            'content': content,
            'mode': 'range',
            'pages_per_file': pages_per_file,
            'page_range': page_range,
            'filename': filename
        })
    else:
        # Markers mode - split at specified points
        result = splitter.process(None, {
            'content': content,
            'mode': 'markers',
            'split_points': split_points,
            'filename': filename
        })
    
    if not result.success:
        return APIResponse.error(result.error, 'SPLIT_ERROR')
    
    return send_file(
        result.output,
        as_attachment=True,
        download_name=result.filename,
        mimetype=result.mimetype
    )


@pdf_tools_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """
    Get supported formats for PDF operations.
    
    Returns:
        JSON with supported formats
    """
    return APIResponse.success({
        'merge': {
            'formats': merger.get_supported_formats(),
            'description': merger.description
        },
        'split': {
            'formats': splitter.get_supported_formats(),
            'description': splitter.description
        }
    })
