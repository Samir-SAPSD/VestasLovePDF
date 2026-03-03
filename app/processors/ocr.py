# -*- coding: utf-8 -*-
"""
OCR Processor - Strategy implementation for OCR operations.
"""
from typing import List
from app.processors.base import FileProcessor, ProcessResult, ProcessorRegistry

# Import existing OCR functions
from app.utils.ocr_pdf import (
    check_tesseract_installed,
    get_available_languages,
    ocr_pdf_to_text,
    ocr_pdf_to_searchable_pdf,
    ocr_pdf_to_txt,
    ocr_pdf_to_docx,
    get_pdf_preview_for_ocr
)
from app.utils.pdf_merger import get_pdf_page_count


@ProcessorRegistry.register('ocr')
class OCRProcessor(FileProcessor):
    """
    Processor for OCR (Optical Character Recognition) on PDFs.
    """
    
    name = "ocr"
    description = "Extrai texto de PDFs escaneados usando OCR"
    supported_formats = ['.pdf']
    
    def __init__(self):
        super().__init__()
        self._tesseract_status = None
    
    def validate(self, file, options: dict = None) -> tuple:
        if not file or not file.filename:
            return False, "Arquivo não fornecido"
        
        ext = self.get_file_extension(file.filename)
        if ext != '.pdf':
            return False, "Apenas arquivos PDF são aceitos para OCR"
        
        # Check if Tesseract is installed
        status = self.check_tesseract()
        if not status.get('installed'):
            return False, "Tesseract OCR não está instalado ou configurado"
        
        return True, None
    
    def process(self, file, options: dict = None) -> ProcessResult:
        """
        Perform OCR on PDF.
        
        Options:
            language: OCR language (default: 'por')
            dpi: Resolution for OCR (default: 300)
            output_format: 'txt', 'docx', or 'pdf' (default: 'txt')
        """
        options = options or {}
        lang = options.get('language', 'por')
        dpi = options.get('dpi', 300)
        output_format = options.get('output_format', 'txt')
        
        try:
            original_size = self.get_file_size(file)
            
            if output_format == 'txt':
                output, filename, mimetype = ocr_pdf_to_txt(file, lang=lang, dpi=dpi)
            elif output_format == 'docx':
                output, filename, mimetype = ocr_pdf_to_docx(file, lang=lang, dpi=dpi)
            elif output_format == 'pdf':
                output, filename, mimetype = ocr_pdf_to_searchable_pdf(file, lang=lang, dpi=dpi)
            else:
                return ProcessResult.failure(f"Formato de saída inválido: {output_format}")
            
            output.seek(0, 2)
            processed_size = output.tell()
            output.seek(0)
            
            return ProcessResult(
                success=True,
                output=output,
                filename=filename,
                mimetype=mimetype,
                original_size=original_size,
                processed_size=processed_size,
                metadata={
                    'language': lang,
                    'dpi': dpi,
                    'output_format': output_format,
                    'operation': 'ocr'
                }
            )
        except Exception as e:
            return ProcessResult.failure(str(e))
    
    def extract_text(self, file, options: dict = None) -> dict:
        """
        Extract text from PDF using OCR (returns JSON result).
        
        Options:
            language: OCR language
            dpi: Resolution
        """
        options = options or {}
        lang = options.get('language', 'por')
        dpi = options.get('dpi', 300)
        
        return ocr_pdf_to_text(file, lang=lang, dpi=dpi)
    
    def check_tesseract(self) -> dict:
        """Check if Tesseract is installed and configured."""
        if self._tesseract_status is None:
            self._tesseract_status = check_tesseract_installed()
        return self._tesseract_status
    
    def get_available_languages(self) -> dict:
        """Get available OCR languages."""
        return get_available_languages()
    
    def get_preview(self, file_content: bytes, page_number: int = 0, zoom: float = 0.4) -> str:
        """Get base64 preview of a PDF page."""
        return get_pdf_preview_for_ocr(file_content, page_number, zoom)
    
    def get_page_count(self, file_content: bytes) -> int:
        """Get number of pages in a PDF."""
        return get_pdf_page_count(file_content)
