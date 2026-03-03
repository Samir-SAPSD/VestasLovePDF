# -*- coding: utf-8 -*-
"""
Middleware and decorators for API endpoints.
"""
from functools import wraps
from flask import request
from app.core.response import APIResponse
from app.core.exceptions import ValidationError, FileTooLargeError


def validate_file_upload(allowed_extensions: list = None, max_size_mb: int = 50):
    """
    Decorator to validate file uploads.
    
    Args:
        allowed_extensions: List of allowed file extensions (e.g., ['.pdf', '.jpg'])
        max_size_mb: Maximum file size in MB
        
    Usage:
        @validate_file_upload(allowed_extensions=['.pdf'], max_size_mb=100)
        def upload_pdf():
            file = request.files['file']
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if file is present
            if 'file' not in request.files:
                return APIResponse.error(
                    'Nenhum arquivo enviado',
                    'NO_FILE',
                    400
                )
            
            file = request.files['file']
            
            if file.filename == '':
                return APIResponse.error(
                    'Nenhum arquivo selecionado',
                    'EMPTY_FILENAME',
                    400
                )
            
            # Check file extension
            if allowed_extensions:
                import os
                ext = os.path.splitext(file.filename)[1].lower()
                if ext not in allowed_extensions:
                    return APIResponse.error(
                        f'Formato não suportado. Formatos aceitos: {", ".join(allowed_extensions)}',
                        'UNSUPPORTED_FORMAT',
                        415
                    )
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            size = file.tell()
            file.seek(0)  # Reset to beginning
            
            max_size_bytes = max_size_mb * 1024 * 1024
            if size > max_size_bytes:
                return APIResponse.error(
                    f'Arquivo muito grande. Máximo: {max_size_mb}MB',
                    'FILE_TOO_LARGE',
                    413
                )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_json_body(required_fields: list = None):
    """
    Decorator to validate JSON request body.
    
    Args:
        required_fields: List of required field names
        
    Usage:
        @validate_json_body(required_fields=['content', 'fileName'])
        def process_data():
            data = request.get_json()
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if data is None:
                return APIResponse.error(
                    'Body JSON inválido ou ausente',
                    'INVALID_JSON',
                    400
                )
            
            if required_fields:
                missing = [field for field in required_fields if field not in data]
                if missing:
                    return APIResponse.error(
                        f'Campos obrigatórios ausentes: {", ".join(missing)}',
                        'MISSING_FIELDS',
                        400
                    )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def handle_exceptions(f):
    """
    Decorator to handle exceptions and return standardized error responses.
    
    Usage:
        @handle_exceptions
        def risky_operation():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return APIResponse.error(e.message, e.code, e.status)
        except Exception as e:
            return APIResponse.error(
                str(e),
                'INTERNAL_ERROR',
                500
            )
    return decorated_function
