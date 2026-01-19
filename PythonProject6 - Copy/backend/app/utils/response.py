"""
Shared response utility for consistent API responses across all endpoints.
"""
from flask import jsonify
from http import HTTPStatus


def api_response(status: HTTPStatus, payload: dict):
    """
    Create a standardized JSON response for API endpoints.
    
    Args:
        status: HTTPStatus enum value
        payload: Dictionary containing response data
        
    Returns:
        Tuple of (jsonify response, status code)
    """
    return jsonify({
        "http": {
            "code": status.value,
            "name": status.name,
            "message": status.phrase
        },
        **payload
    }), status.value
