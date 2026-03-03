# -*- coding: utf-8 -*-
"""
Converter Processor - Strategy implementation for file conversion.
"""
from typing import List
from app.processors.base import FileProcessor, ProcessResult, ProcessorRegistry

# Import existing conversion functions
from app.utils.converters import (
    convert_file,
    detect_excel_version,
    get_available_conversions,
    EXCEL_FORMATS,
    SUPPORTED_IMAGE_FORMATS,
    MIMETYPES
)


@ProcessorRegistry.register('converter')
class ConverterProcessor(FileProcessor):
    """
    Processor for converting files between formats.
    Supports: Images to PDF, PDF to Images, Excel to various formats.
    """
    
    name = "converter"
    description = "Converte arquivos entre formatos (PDF, Imagens, Excel)"
    supported_formats = [
        '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
        '.xlsx', '.xls', '.xlsb', '.ods', '.docx'
    ]
    
    def validate(self, file, options: dict = None) -> tuple:
        if not file or not file.filename:
            return False, "Arquivo não fornecido"
        
        ext = self.get_file_extension(file.filename)
        if ext not in self.supported_formats:
            return False, f"Formato {ext} não suportado"
        
        options = options or {}
        conv_type = options.get('conv_type')
        
        if not conv_type:
            return False, "Tipo de conversão não especificado"
        
        return True, None
    
    def process(self, file, options: dict = None) -> ProcessResult:
        """
        Convert file based on specified conversion type.
        
        Options:
            conv_type: Conversion type (e.g., 'img_to_pdf', 'pdf_to_jpg', 'excel_to_csv')
        """
        options = options or {}
        conv_type = options.get('conv_type')
        
        if not conv_type:
            return ProcessResult.failure("Tipo de conversão não especificado")
        
        try:
            original_size = self.get_file_size(file)
            output, filename, mimetype = convert_file(file, conv_type)
            
            # Get processed size
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
                    'conversion_type': conv_type,
                    'original_format': self.get_file_extension(file.filename),
                    'output_format': self.get_file_extension(filename)
                }
            )
        except Exception as e:
            return ProcessResult.failure(str(e))
    
    def detect_format(self, filename: str) -> dict:
        """
        Detect file format and return available conversions.
        """
        ext = self.get_file_extension(filename)
        
        # Check if it's an Excel file
        excel_info = detect_excel_version(filename)
        if excel_info:
            return excel_info
        
        # Check if it's an image
        if ext in SUPPORTED_IMAGE_FORMATS:
            return {
                'extension': ext,
                'format': 'Image',
                'available_conversions': [
                    {'value': 'img_to_pdf', 'label': 'Converter para PDF'}
                ]
            }
        
        # Check if it's a PDF
        if ext == '.pdf':
            return {
                'extension': ext,
                'format': 'PDF',
                'available_conversions': [
                    {'value': 'pdf_to_jpg', 'label': 'Converter para JPG'},
                    {'value': 'pdf_to_png', 'label': 'Converter para PNG'},
                    {'value': 'pdf_to_webp', 'label': 'Converter para WebP'},
                ]
            }
        
        return None


@ProcessorRegistry.register('excel_converter')
class ExcelConverterProcessor(FileProcessor):
    """
    Specialized processor for Excel file conversions.
    """
    
    name = "excel_converter"
    description = "Converte arquivos Excel entre formatos"
    supported_formats = ['.xlsx', '.xls', '.xlsb', '.ods']
    
    def validate(self, file, options: dict = None) -> tuple:
        if not file or not file.filename:
            return False, "Arquivo não fornecido"
        
        ext = self.get_file_extension(file.filename)
        if ext not in self.supported_formats:
            return False, f"Formato {ext} não é um arquivo Excel válido"
        
        return True, None
    
    def process(self, file, options: dict = None) -> ProcessResult:
        options = options or {}
        conv_type = options.get('conv_type')
        
        if not conv_type:
            return ProcessResult.failure("Tipo de conversão não especificado")
        
        try:
            original_size = self.get_file_size(file)
            output, filename, mimetype = convert_file(file, conv_type)
            
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
                metadata={'conversion_type': conv_type}
            )
        except Exception as e:
            return ProcessResult.failure(str(e))
    
    def get_conversions_for_file(self, filename: str) -> dict:
        """Get available conversions for an Excel file."""
        return detect_excel_version(filename)


@ProcessorRegistry.register('image_converter')
class ImageConverterProcessor(FileProcessor):
    """
    Specialized processor for image conversions.
    """
    
    name = "image_converter"
    description = "Converte imagens para PDF"
    supported_formats = SUPPORTED_IMAGE_FORMATS
    
    def validate(self, file, options: dict = None) -> tuple:
        if not file or not file.filename:
            return False, "Arquivo não fornecido"
        
        ext = self.get_file_extension(file.filename)
        if ext not in self.supported_formats:
            return False, f"Formato {ext} não é uma imagem válida"
        
        return True, None
    
    def process(self, file, options: dict = None) -> ProcessResult:
        try:
            original_size = self.get_file_size(file)
            output, filename, mimetype = convert_file(file, 'img_to_pdf')
            
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
                metadata={'conversion_type': 'img_to_pdf'}
            )
        except Exception as e:
            return ProcessResult.failure(str(e))
