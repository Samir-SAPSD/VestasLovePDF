# -*- coding: utf-8 -*-
"""
Compressor Processor - Strategy implementation for file compression.
"""
from typing import List
from app.processors.base import FileProcessor, ProcessResult, ProcessorRegistry

# Import existing compression functions
from app.utils.compressor import (
    compress_file,
    compress_image,
    compress_pdf,
    compress_to_zip,
    estimate_compression,
    calculate_quality_for_target_size
)


@ProcessorRegistry.register('compressor')
class CompressorProcessor(FileProcessor):
    """
    Processor for compressing images, PDFs, and other files.
    """
    
    name = "compressor"
    description = "Comprime imagens, PDFs e outros arquivos"
    supported_formats = [
        '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff', '.tif',
        '.pdf', '*'  # * indicates any file (will be zipped)
    ]
    
    def validate(self, file, options: dict = None) -> tuple:
        """
        Validate the file for compression.
        All files are valid since unsupported formats will be zipped.
        """
        if not file or not file.filename:
            return False, "Arquivo não fornecido"
        
        return True, None
    
    def process(self, file, options: dict = None) -> ProcessResult:
        """
        Compress the file based on type and options.
        
        Options:
            compression_type: 'auto', 'image', 'pdf', 'zip'
            quality: 1-100 (default: 85)
        """
        options = options or {}
        compression_type = options.get('compression_type', 'auto')
        quality = options.get('quality', 85)
        
        try:
            output, filename, mimetype, original_size, compressed_size, ratio = compress_file(
                file, compression_type, quality
            )
            
            return ProcessResult(
                success=True,
                output=output,
                filename=filename,
                mimetype=mimetype,
                original_size=original_size,
                processed_size=compressed_size,
                metadata={
                    'compression_type': compression_type,
                    'quality': quality,
                    'ratio_percentage': round(ratio, 2)
                }
            )
        except Exception as e:
            return ProcessResult.failure(str(e))
    
    def estimate(self, file, options: dict = None) -> dict:
        """
        Estimate compression result without actually compressing.
        
        Returns dict with estimated sizes and compression ratio.
        """
        options = options or {}
        compression_type = options.get('compression_type', 'auto')
        quality = options.get('quality', 85)
        
        return estimate_compression(file, compression_type, quality)
    
    def calculate_quality_for_target(self, file, target_size_bytes: int, compression_type: str = 'auto') -> dict:
        """
        Calculate required quality to achieve target file size.
        """
        return calculate_quality_for_target_size(file, target_size_bytes, compression_type)


@ProcessorRegistry.register('image_compressor')
class ImageCompressorProcessor(FileProcessor):
    """
    Specialized processor for image compression only.
    """
    
    name = "image_compressor"
    description = "Comprime imagens (JPG, PNG, WebP)"
    supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff', '.tif']
    
    def validate(self, file, options: dict = None) -> tuple:
        if not file or not file.filename:
            return False, "Arquivo não fornecido"
        
        ext = self.get_file_extension(file.filename)
        if ext not in self.supported_formats:
            return False, f"Formato {ext} não suportado. Use: {', '.join(self.supported_formats)}"
        
        return True, None
    
    def process(self, file, options: dict = None) -> ProcessResult:
        options = options or {}
        quality = options.get('quality', 85)
        
        try:
            output, filename, mimetype, original_size, compressed_size, ratio = compress_image(
                file, quality
            )
            
            return ProcessResult(
                success=True,
                output=output,
                filename=filename,
                mimetype=mimetype,
                original_size=original_size,
                processed_size=compressed_size,
                metadata={'quality': quality}
            )
        except Exception as e:
            return ProcessResult.failure(str(e))


@ProcessorRegistry.register('pdf_compressor')
class PDFCompressorProcessor(FileProcessor):
    """
    Specialized processor for PDF compression only.
    """
    
    name = "pdf_compressor"
    description = "Comprime documentos PDF"
    supported_formats = ['.pdf']
    
    def validate(self, file, options: dict = None) -> tuple:
        if not file or not file.filename:
            return False, "Arquivo não fornecido"
        
        ext = self.get_file_extension(file.filename)
        if ext != '.pdf':
            return False, "Apenas arquivos PDF são aceitos"
        
        return True, None
    
    def process(self, file, options: dict = None) -> ProcessResult:
        options = options or {}
        quality = options.get('quality', 75)
        
        try:
            output, filename, mimetype, original_size, compressed_size, ratio = compress_pdf(
                file, quality
            )
            
            return ProcessResult(
                success=True,
                output=output,
                filename=filename,
                mimetype=mimetype,
                original_size=original_size,
                processed_size=compressed_size,
                metadata={'quality': quality}
            )
        except Exception as e:
            return ProcessResult.failure(str(e))
