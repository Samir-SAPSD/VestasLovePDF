# -*- coding: utf-8 -*-
"""
Pages Blueprint - Serves HTML templates.
This blueprint handles the frontend pages (templates).
"""
from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def home():
    """Home page."""
    return render_template('home.html')


@pages_bp.route('/converter')
def converter():
    """File converter page."""
    return render_template('converter.html')


@pages_bp.route('/excel-converter')
def excel_converter():
    """Excel converter page."""
    return render_template('excel_converter.html')


@pages_bp.route('/compressor')
def compressor():
    """File compressor page."""
    return render_template('compressor.html')


@pages_bp.route('/pdf-merger')
def pdf_merger():
    """PDF merger page."""
    return render_template('pdf_merger.html')


@pages_bp.route('/pdf-splitter')
def pdf_splitter():
    """PDF splitter page."""
    return render_template('pdf_splitter.html')


@pages_bp.route('/ocr-pdf')
def ocr_pdf():
    """OCR PDF page."""
    return render_template('ocr_pdf.html')
