# -*- coding: utf-8 -*-
"""
VestasLovePDF - Main Application Entry Point

This module serves as the main entry point for the application.
It uses the application factory pattern and registers all blueprints.

Architecture:
    - app/__init__.py: Application factory (create_app)
    - app/api/v1/: API endpoints (Blueprint pattern)
    - app/processors/: File processors (Strategy pattern)
    - app/core/: Core utilities (response, exceptions, middleware)
    - app/pages/: Template rendering routes
    - app/utils/: Legacy utility functions (still used by processors)

API Endpoints:
    - /api/v1/compress/*: Compression endpoints
    - /api/v1/convert/*: Conversion endpoints
    - /api/v1/pdf/*: PDF tools (merge, split)
    - /api/v1/ocr/*: OCR endpoints

Legacy Routes (for backward compatibility):
    - /convert, /compress, etc. still work with the old frontend
"""
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
import os
import webbrowser
from threading import Timer, Thread
import time
import base64
import zipfile

# Import utilities (for legacy routes compatibility)
from app.utils.converters import convert_file, detect_excel_version
from app.utils.compressor import compress_file, estimate_compression, calculate_quality_for_target_size
from app.utils.pdf_merger import get_pdf_preview, get_pdf_page_count, merge_pdfs, get_all_pdf_previews, split_pdf
from app.utils.ocr_pdf import (
    check_tesseract_installed,
    get_available_languages,
    ocr_pdf_to_text,
    ocr_pdf_to_searchable_pdf,
    ocr_pdf_to_txt,
    ocr_pdf_to_docx,
    get_pdf_preview_for_ocr
)

# Import API blueprints
from app.api.v1 import api_v1
from app.core.response import APIResponse
from app.core.exceptions import AppException

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

# Enable CORS for API endpoints
try:
    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
except ImportError:
    pass  # CORS not installed, skip

# Register API v1 blueprint
app.register_blueprint(api_v1, url_prefix='/api/v1')

# Register global error handlers for API
@app.errorhandler(AppException)
def handle_app_exception(error):
    return APIResponse.error(error.message, error.code, error.status)

# Heartbeat monitoring for desktop mode
last_heartbeat = time.time()

def monitor_heartbeat():
    """Monitor heartbeat from browser for desktop mode."""
    global last_heartbeat
    while True:
        time.sleep(1)
        if time.time() - last_heartbeat > 5:
            print("Nenhum heartbeat recebido. Encerrando servidor...")
            os._exit(0)

def open_browser():
    """Open browser automatically for desktop mode."""
    webbrowser.open_new_tab("http://127.0.0.1:5000")


# ==================== LEGACY PAGE ROUTES ====================
# These routes serve the HTML templates (frontend pages)
# They are kept for backward compatibility with the current frontend

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/converter')
def converter():
    return render_template('converter.html')

@app.route('/excel-converter')
def excel_converter():
    return render_template('excel_converter.html')

@app.route('/compressor')
def compressor():
    return render_template('compressor.html')

@app.route('/pdf-merger')
def pdf_merger():
    return render_template('pdf_merger.html')

@app.route('/pdf-splitter')
def pdf_splitter():
    return render_template('pdf_splitter.html')

@app.route('/ocr-pdf')
def ocr_pdf():
    return render_template('ocr_pdf.html')


# ==================== LEGACY API ROUTES ====================
# These routes are kept for backward compatibility with the current frontend.
# New implementations should use the API v1 endpoints (/api/v1/*)
#
# Mapping of legacy routes to new API endpoints:
#   /pdf-splitter/load  -> POST /api/v1/pdf/split/load
#   /pdf-splitter/split -> POST /api/v1/pdf/split
#   /pdf-merger/preview -> POST /api/v1/pdf/merge/preview
#   /pdf-merger/merge   -> POST /api/v1/pdf/merge
#   /convert            -> POST /api/v1/convert/
#   /compress           -> POST /api/v1/compress/
#   /estimate-compression -> POST /api/v1/compress/estimate
#   /calculate-target-quality -> POST /api/v1/compress/target-quality
#   /detect-excel       -> POST /api/v1/convert/excel/detect
#   /ocr/*              -> /api/v1/ocr/*

@app.route('/pdf-splitter/load', methods=['POST'])
def pdf_splitter_load():
    """Carrega todas as páginas do PDF para preview."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    try:
        content = file.read()
        previews = get_all_pdf_previews(content, zoom=0.4)
        pages = get_pdf_page_count(content)
        return jsonify({'previews': previews, 'pages': pages})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pdf-splitter/split', methods=['POST'])
def pdf_split():
    """Separa o PDF em múltiplos arquivos."""
    try:
        data = request.get_json()
        content = base64.b64decode(data.get('content', ''))
        split_points = data.get('splitPoints', [])
        original_filename = data.get('fileName', 'documento')
        
        if not content:
            return jsonify({'error': 'Conteúdo do PDF não fornecido'}), 400
        
        if not split_points:
            return jsonify({'error': 'Nenhum ponto de separação definido'}), 400
        
        # Split the PDF
        pdf_parts = split_pdf(content, split_points)
        
        # Create ZIP file with all parts
        from io import BytesIO
        zip_buffer = BytesIO()
        
        base_name = original_filename.replace('.pdf', '').replace('.PDF', '')
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, (pdf_io, _) in enumerate(pdf_parts):
                pdf_io.seek(0)
                zip_file.writestr(f"{base_name}_parte_{idx + 1}.pdf", pdf_io.read())
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f"{base_name}_separado.zip",
            mimetype='application/zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pdf-merger/preview', methods=['POST'])
def pdf_preview():
    """Gera preview da primeira página do PDF."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    try:
        content = file.read()
        preview = get_pdf_preview(content, page_number=0, zoom=0.5)
        pages = get_pdf_page_count(content)
        return jsonify({'preview': preview, 'pages': pages})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pdf-merger/merge', methods=['POST'])
def pdf_merge():
    """Unifica múltiplos PDFs."""
    try:
        data = request.get_json()
        files = data.get('files', [])
        
        if len(files) < 2:
            return jsonify({'error': 'É necessário pelo menos 2 arquivos para unificar'}), 400
        
        pdf_list = []
        for file_data in files:
            content = base64.b64decode(file_data['content'])
            rotation = file_data.get('rotation', 0)
            pdf_list.append({'content': content, 'rotation': rotation})
        
        output, filename, mimetype = merge_pdfs(pdf_list)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    global last_heartbeat
    last_heartbeat = time.time()
    return 'OK'

@app.route('/detect-excel', methods=['POST'])
def detect_excel():
    """Detecta a versão do arquivo Excel e retorna opções de conversão."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    result = detect_excel_version(file.filename)
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Formato de arquivo não reconhecido'}), 400

@app.route('/convert', methods=['POST'])
def convert():
    # Determinar de qual página veio a requisição
    referer = request.headers.get('Referer', '')
    if 'excel-converter' in referer:
        redirect_page = 'excel_converter'
    elif 'converter' in referer:
        redirect_page = 'converter'
    else:
        redirect_page = 'index'
    
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado')
        return redirect(url_for(redirect_page))
    
    file = request.files['file']
    conv_type = request.form.get('conv_type')
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado')
        return redirect(url_for(redirect_page))
    
    try:
        output, output_filename, mimetype = convert_file(file, conv_type)
        return send_file(
            output,
            as_attachment=True,
            download_name=output_filename,
            mimetype=mimetype
        )
    except Exception as e:
        flash(f'Erro na conversão: {e}')
        return redirect(url_for(redirect_page))

@app.route('/compress', methods=['POST'])
def compress():
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado')
        return redirect(url_for('compressor'))
    
    file = request.files['file']
    compression_type = request.form.get('compression_type', 'auto')
    quality = int(request.form.get('quality', 85))
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado')
        return redirect(url_for('compressor'))
    
    try:
        output, output_filename, mimetype, original_size, compressed_size, ratio = compress_file(
            file, compression_type, quality
        )
        return send_file(
            output,
            as_attachment=True,
            download_name=output_filename,
            mimetype=mimetype
        )
    except Exception as e:
        flash(f'Erro na compressão: {e}')
        return redirect(url_for('compressor'))

@app.route('/estimate-compression', methods=['POST'])
def estimate_compression_route():
    """Estima o tamanho final após compressão."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    compression_type = request.form.get('compression_type', 'auto')
    quality = int(request.form.get('quality', 85))
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    try:
        result = estimate_compression(file, compression_type, quality)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculate-target-quality', methods=['POST'])
def calculate_target_quality():
    """Calcula a qualidade necessária para atingir um tamanho alvo."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    target_size = request.form.get('target_size', 0)
    target_unit = request.form.get('target_unit', 'KB')
    compression_type = request.form.get('compression_type', 'auto')
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    try:
        # Converter tamanho para bytes
        target_size = float(target_size)
        if target_unit == 'KB':
            target_size_bytes = int(target_size * 1024)
        elif target_unit == 'MB':
            target_size_bytes = int(target_size * 1024 * 1024)
        else:
            target_size_bytes = int(target_size)
        
        result = calculate_quality_for_target_size(file, target_size_bytes, compression_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ROTAS OCR ====================

@app.route('/ocr/check')
def ocr_check():
    """Verifica se o Tesseract está instalado."""
    return jsonify(check_tesseract_installed())


@app.route('/ocr/languages')
def ocr_languages():
    """Retorna idiomas disponíveis para OCR."""
    return jsonify(get_available_languages())


@app.route('/ocr/preview', methods=['POST'])
def ocr_preview():
    """Gera preview de um PDF para OCR."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    try:
        content = file.read()
        preview = get_pdf_preview_for_ocr(content, page_number=0, zoom=0.4)
        pages = get_pdf_page_count(content)
        return jsonify({'preview': preview, 'pages': pages})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ocr/extract', methods=['POST'])
def ocr_extract():
    """Extrai texto de um PDF usando OCR (retorna JSON)."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    lang = request.form.get('language', 'por')
    dpi = int(request.form.get('dpi', 300))
    
    try:
        result = ocr_pdf_to_text(file, lang=lang, dpi=dpi)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ocr/convert', methods=['POST'])
def ocr_convert():
    """Converte PDF para formato com OCR."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    lang = request.form.get('language', 'por')
    dpi = int(request.form.get('dpi', 300))
    output_format = request.form.get('output_format', 'txt')
    
    try:
        if output_format == 'txt':
            output, filename, mimetype = ocr_pdf_to_txt(file, lang=lang, dpi=dpi)
        elif output_format == 'docx':
            output, filename, mimetype = ocr_pdf_to_docx(file, lang=lang, dpi=dpi)
        elif output_format == 'pdf':
            output, filename, mimetype = ocr_pdf_to_searchable_pdf(file, lang=lang, dpi=dpi)
        else:
            return jsonify({'error': 'Formato de saída inválido'}), 400
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def run_app():
    monitor_thread = Thread(target=monitor_heartbeat)
    monitor_thread.daemon = True
    monitor_thread.start()

    Timer(1.5, open_browser).start()
    app.run(debug=False, port=5000)
