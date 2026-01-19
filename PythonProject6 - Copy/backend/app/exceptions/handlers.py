"""
Error handlers for Flask application.
Demonstrates separation of concerns: validation errors vs business exceptions.
"""
from flask import jsonify
from http import HTTPStatus
import logging
import traceback

from backend.app.exceptions.exceptions import AppError, NotFoundError, DuplicateError

# Configure logging
logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """
    Register error handlers for the Flask application.
    
    Error mapping:
    - ValidationError (Pydantic) → 422 Unprocessable Entity
    - NotFoundError → 404 Not Found
    - DuplicateError → 409 Conflict
    - AppError (business logic) → 400 Bad Request
    - Generic exceptions → 500 Internal Server Error
    """

    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        """Handle 404 Not Found errors."""
        logger.info(f"Resource not found: {e.message}")
        return jsonify({
            "http": {
                "code": HTTPStatus.NOT_FOUND.value,
                "name": HTTPStatus.NOT_FOUND.name,
                "message": HTTPStatus.NOT_FOUND.phrase
            },
            "success": False,
            "error": e.message
        }), HTTPStatus.NOT_FOUND.value

    @app.errorhandler(DuplicateError)
    def handle_duplicate(e):
        """Handle 409 Conflict errors (duplicate resources)."""
        logger.info(f"Duplicate resource: {e.message}")
        return jsonify({
            "http": {
                "code": HTTPStatus.CONFLICT.value,
                "name": HTTPStatus.CONFLICT.name,
                "message": HTTPStatus.CONFLICT.phrase
            },
            "success": False,
            "error": e.message
        }), HTTPStatus.CONFLICT.value

    @app.errorhandler(AppError)
    def handle_app_error(e):
        """
        Handle application errors.
        Distinguishes between validation errors (422) and business logic errors (400).
        """
        # Check if it's a validation error (Pydantic errors are lists/dicts)
        if isinstance(e.message, (list, dict)):
            # Validation error → 422 Unprocessable Entity
            logger.warning(f"Validation error: {e.message}")
            return jsonify({
                "http": {
                    "code": HTTPStatus.UNPROCESSABLE_ENTITY.value,
                    "name": HTTPStatus.UNPROCESSABLE_ENTITY.name,
                    "message": HTTPStatus.UNPROCESSABLE_ENTITY.phrase
                },
                "success": False,
                "error": "Validation error",
                "details": e.message
            }), HTTPStatus.UNPROCESSABLE_ENTITY.value
        else:
            # Business logic error → 400 Bad Request
            logger.warning(f"Business logic error: {e.message}")
            return jsonify({
                "http": {
                    "code": HTTPStatus.BAD_REQUEST.value,
                    "name": HTTPStatus.BAD_REQUEST.name,
                    "message": HTTPStatus.BAD_REQUEST.phrase
                },
                "success": False,
                "error": e.message
            }), HTTPStatus.BAD_REQUEST.value

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Handle all unhandled exceptions - return JSON instead of HTML."""
        error_trace = traceback.format_exc()
        logger.error(f"Unhandled exception: {error_trace}")
        
        # If it's one of our custom exceptions, let the specific handler deal with it
        if isinstance(e, (AppError, NotFoundError, DuplicateError)):
            raise  # Re-raise to let specific handler catch it
        
        return jsonify({
            "http": {
                "code": HTTPStatus.INTERNAL_SERVER_ERROR.value,
                "name": HTTPStatus.INTERNAL_SERVER_ERROR.name,
                "message": HTTPStatus.INTERNAL_SERVER_ERROR.phrase
            },
            "success": False,
            "error": f"An internal server error occurred: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR.value

    @app.errorhandler(500)
    def handle_internal_error(e):
        """Handle 500 Internal Server Error - return JSON instead of HTML."""
        error_trace = traceback.format_exc()
        logger.error(f"Internal Server Error: {error_trace}")
        
        return jsonify({
            "http": {
                "code": HTTPStatus.INTERNAL_SERVER_ERROR.value,
                "name": HTTPStatus.INTERNAL_SERVER_ERROR.name,
                "message": HTTPStatus.INTERNAL_SERVER_ERROR.phrase
            },
            "success": False,
            "error": "An internal server error occurred. Please try again later."
        }), HTTPStatus.INTERNAL_SERVER_ERROR.value
