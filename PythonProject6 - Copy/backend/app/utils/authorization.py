"""
Authorization utilities for role-based access control.
"""
from functools import wraps
from flask import request, jsonify
from http import HTTPStatus
import logging

from backend.app.exceptions.exceptions import AppError

logger = logging.getLogger(__name__)


def require_role(*allowed_roles):
    """
    Decorator to require specific roles for API endpoints.
    
    Usage:
        @require_role('admin')
        def admin_only_endpoint():
            ...
    
        @require_role('admin', 'trainer')
        def admin_or_trainer_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get role from request (would typically come from auth token/session)
            # For now, check if role is in headers or query params
            role = request.headers.get('X-User-Role') or request.args.get('role')
            
            if not role:
                return jsonify({
                    "http": {
                        "code": HTTPStatus.UNAUTHORIZED.value,
                        "name": HTTPStatus.UNAUTHORIZED.name,
                        "message": HTTPStatus.UNAUTHORIZED.phrase
                    },
                    "success": False,
                    "error": "Role not specified"
                }), HTTPStatus.UNAUTHORIZED.value
            
            if role not in allowed_roles:
                return jsonify({
                    "http": {
                        "code": HTTPStatus.FORBIDDEN.value,
                        "name": HTTPStatus.FORBIDDEN.name,
                        "message": HTTPStatus.FORBIDDEN.phrase
                    },
                    "success": False,
                    "error": f"Access denied. Required role: {', '.join(allowed_roles)}"
                }), HTTPStatus.FORBIDDEN.value
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_trainer_ownership(trainer_id_param='trainer_id'):
    """
    Decorator to ensure trainer can only access their own resources.
    
    Usage:
        @require_trainer_ownership('trainer_id')
        def get_trainer_sessions(trainer_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current user's trainer_id from auth context
            current_trainer_id = request.headers.get('X-Trainer-ID') or request.args.get('current_trainer_id')
            requested_trainer_id = kwargs.get(trainer_id_param) or request.args.get(trainer_id_param)
            
            if not current_trainer_id:
                return jsonify({
                    "http": {
                        "code": HTTPStatus.UNAUTHORIZED.value,
                        "name": HTTPStatus.UNAUTHORIZED.name,
                        "message": HTTPStatus.UNAUTHORIZED.phrase
                    },
                    "success": False,
                    "error": "Trainer ID not specified"
                }), HTTPStatus.UNAUTHORIZED.value
            
            # Admin can access any trainer's resources
            role = request.headers.get('X-User-Role') or request.args.get('role')
            if role == 'admin':
                return f(*args, **kwargs)
            
            # Trainer can only access their own resources
            if current_trainer_id != requested_trainer_id:
                return jsonify({
                    "http": {
                        "code": HTTPStatus.FORBIDDEN.value,
                        "name": HTTPStatus.FORBIDDEN.name,
                        "message": HTTPStatus.FORBIDDEN.phrase
                    },
                    "success": False,
                    "error": "Access denied. You can only access your own resources."
                }), HTTPStatus.FORBIDDEN.value
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_member_ownership(member_id_param='member_id'):
    """
    Decorator to ensure member can only access their own resources.
    Admin and trainers (for their trainees) can also access.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current user's member_id from auth context
            current_member_id = request.headers.get('X-Member-ID') or request.args.get('current_member_id')
            requested_member_id = kwargs.get(member_id_param) or request.args.get(member_id_param)
            
            role = request.headers.get('X-User-Role') or request.args.get('role')
            
            # Admin can access any member's resources
            if role == 'admin':
                return f(*args, **kwargs)
            
            # Trainer can access their trainees' resources (would need to check trainer-member relationship)
            if role == 'trainer':
                # For now, allow - in production, verify trainer-member relationship
                return f(*args, **kwargs)
            
            # Member can only access their own resources
            if not current_member_id:
                return jsonify({
                    "http": {
                        "code": HTTPStatus.UNAUTHORIZED.value,
                        "name": HTTPStatus.UNAUTHORIZED.name,
                        "message": HTTPStatus.UNAUTHORIZED.phrase
                    },
                    "success": False,
                    "error": "Member ID not specified"
                }), HTTPStatus.UNAUTHORIZED.value
            
            if current_member_id != requested_member_id:
                return jsonify({
                    "http": {
                        "code": HTTPStatus.FORBIDDEN.value,
                        "name": HTTPStatus.FORBIDDEN.name,
                        "message": HTTPStatus.FORBIDDEN.phrase
                    },
                    "success": False,
                    "error": "Access denied. You can only access your own resources."
                }), HTTPStatus.FORBIDDEN.value
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
