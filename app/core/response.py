# -*- coding: utf-8 -*-
"""
Standardized API Response Pattern.
Ensures consistent JSON responses across all endpoints.
"""
from flask import jsonify
from typing import Any, Optional


class APIResponse:
    """
    Standardized API response builder.
    
    Usage:
        return APIResponse.success({'file_url': url})
        return APIResponse.error('Invalid file', 'VALIDATION_ERROR', 400)
    """
    
    @staticmethod
    def success(
        data: Any = None, 
        message: Optional[str] = None, 
        status: int = 200
    ):
        """
        Returns a successful JSON response.
        
        Args:
            data: Response data (dict, list, or any serializable object)
            message: Optional success message
            status: HTTP status code (default: 200)
            
        Returns:
            Tuple of (jsonify response, status code)
        """
        response = {
            'success': True,
            'data': data
        }
        if message:
            response['message'] = message
        return jsonify(response), status
    
    @staticmethod
    def error(
        message: str, 
        code: str = 'ERROR', 
        status: int = 400,
        details: Optional[dict] = None
    ):
        """
        Returns an error JSON response.
        
        Args:
            message: Error message
            code: Error code for client identification
            status: HTTP status code (default: 400)
            details: Optional additional error details
            
        Returns:
            Tuple of (jsonify response, status code)
        """
        error_obj = {
            'code': code,
            'message': message
        }
        if details:
            error_obj['details'] = details
            
        return jsonify({
            'success': False,
            'error': error_obj
        }), status
    
    @staticmethod
    def file_response(
        file_data: dict,
        message: Optional[str] = None
    ):
        """
        Returns a response for file operations.
        
        Args:
            file_data: Dict containing file info (filename, size, url, etc.)
            message: Optional success message
            
        Returns:
            Tuple of (jsonify response, status code)
        """
        return APIResponse.success(
            data={'file': file_data},
            message=message
        )
    
    @staticmethod
    def paginated(
        items: list,
        page: int,
        per_page: int,
        total: int
    ):
        """
        Returns a paginated response.
        
        Args:
            items: List of items for current page
            page: Current page number
            per_page: Items per page
            total: Total number of items
            
        Returns:
            Tuple of (jsonify response, status code)
        """
        return APIResponse.success({
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
