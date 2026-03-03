# -*- coding: utf-8 -*-
"""
Custom Exceptions for the application.
All exceptions inherit from AppException for consistent handling.
"""


class AppException(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message: str, code: str = 'ERROR', status: int = 400):
        self.message = message
        self.code = code
        self.status = status
        super().__init__(self.message)


class ValidationError(AppException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, 'VALIDATION_ERROR', 400)


class FileNotFoundError(AppException):
    """Raised when a required file is not found."""
    
    def __init__(self, message: str = 'Arquivo não encontrado'):
        super().__init__(message, 'FILE_NOT_FOUND', 404)


class ProcessingError(AppException):
    """Raised when file processing fails."""
    
    def __init__(self, message: str):
        super().__init__(message, 'PROCESSING_ERROR', 500)


class UnsupportedFormatError(AppException):
    """Raised when file format is not supported."""
    
    def __init__(self, message: str = 'Formato de arquivo não suportado'):
        super().__init__(message, 'UNSUPPORTED_FORMAT', 415)


class ConfigurationError(AppException):
    """Raised when there's a configuration issue (e.g., Tesseract not installed)."""
    
    def __init__(self, message: str):
        super().__init__(message, 'CONFIGURATION_ERROR', 503)


class FileTooLargeError(AppException):
    """Raised when uploaded file exceeds size limit."""
    
    def __init__(self, message: str = 'Arquivo muito grande'):
        super().__init__(message, 'FILE_TOO_LARGE', 413)
