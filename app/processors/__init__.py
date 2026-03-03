# -*- coding: utf-8 -*-
"""
Processors module - Strategy pattern implementation for file processing.
"""
from app.processors.base import FileProcessor, ProcessResult, ProcessorRegistry
from app.processors.compressor import CompressorProcessor, ImageCompressorProcessor, PDFCompressorProcessor
from app.processors.converter import ConverterProcessor, ExcelConverterProcessor, ImageConverterProcessor
from app.processors.pdf_tools import PDFMergerProcessor, PDFSplitterProcessor
from app.processors.ocr import OCRProcessor

__all__ = [
    'FileProcessor',
    'ProcessResult',
    'ProcessorRegistry',
    'CompressorProcessor',
    'ImageCompressorProcessor',
    'PDFCompressorProcessor',
    'ConverterProcessor',
    'ExcelConverterProcessor',
    'ImageConverterProcessor',
    'PDFMergerProcessor',
    'PDFSplitterProcessor',
    'OCRProcessor'
]
