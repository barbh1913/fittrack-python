"""
Flask Blueprint for Admin API endpoints.
Implements: Create admin, Get admin by id, Update admin, List all admins.

This module demonstrates:
- Layer separation: API layer only handles HTTP requests/responses
- Business logic is delegated to Services layer
- Data access is handled by dbhandlers
"""
from flask import Blueprint, request
from http import HTTPStatus
from pydantic import ValidationError
import logging

from backend.app.services.admin_service import AdminService
from backend.app.exceptions.exceptions import AppError, NotFoundError
from backend.app.schemas.admin_schema import AdminCreateRequest, AdminUpdateRequest, AdminResponse
from backend.app.utils.response import api_response

logger = logging.getLogger(__name__)


def create_admins_blueprint(db_manager):
    """
    Interface Layer: Handles HTTP requests/responses, delegates to Business Logic Layer.
    
    Args:
        db_manager: SQLManger instance for database access
        
    Returns:
        Blueprint: Configured Flask Blueprint
    """
    bp = Blueprint("admins", __name__, url_prefix="/api/admins")
    # Use Service Layer (Business Logic) instead of Repository (Data Access)
    svc = AdminService(db_manager)

    @bp.post("")
    def create_admin():
        """
        Create a new admin.
        
        Request Body:
            - id: str (alphanumeric, max 15 chars)
            - fullname: str
            - email: str (validated with regex)
            - phone: str (validated with regex)
            
        Returns:
            201 Created with admin data
        """
        data = request.get_json(silent=True) or {}

        try:
            # Input validation (format, required fields, regex) - handled by Pydantic
            req = AdminCreateRequest.model_validate(data)
        except ValidationError as e:
            # Validation errors translated to HTTP responses
            raise AppError(e.errors())

        # Delegate to Business Logic Layer
        # Service handles: uniqueness check, business rules, orchestrates repository calls
        admin = svc.create_admin(req.id, req.fullname, req.email, req.phone)

        res = AdminResponse(
            id=admin.id,
            fullname=admin.fullname,
            email=admin.email,
            phone=admin.phone
        )

        return api_response(HTTPStatus.CREATED, {
            "success": True,
            **res.model_dump()
        })

    @bp.get("/<admin_id>")
    def get_admin(admin_id: str):
        """
        Get admin by ID.
        
        Args:
            admin_id: Admin ID
            
        Returns:
            200 OK with admin data, or 404 if not found
        """
        try:
            # Delegate to Business Logic Layer
            admin = svc.get_admin(admin_id)

            res = AdminResponse(
                id=admin.id,
                fullname=admin.fullname,
                email=admin.email,
                phone=admin.phone
            )

            return api_response(HTTPStatus.OK, {
                "success": True,
                **res.model_dump()
            })
        except (NotFoundError, AppError):
            raise
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            logger.error(f"Error in get_admin: {error_type}: {error_msg}", exc_info=True)
            
            if "doesn't exist" in error_msg.lower() or "Table" in error_type:
                raise AppError("Database tables not found. Please run 'python seed.py' to create tables and load data.")
            else:
                raise AppError(f"Database error: {error_msg}")

    @bp.get("")
    def list_admins():
        """
        Get all admins.
        
        Returns:
            200 OK with list of all admins
        """
        try:
            admins = svc.get_all_admins()
            admins_list = [
                AdminResponse(
                    id=a.id,
                    fullname=a.fullname,
                    email=a.email,
                    phone=a.phone
                ).model_dump()
                for a in admins
            ]
            
            return api_response(HTTPStatus.OK, {
                "success": True,
                "admins": admins_list,
                "count": len(admins_list)
            })
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in list_admins: {error_msg}", exc_info=True)
            raise AppError(f"Failed to retrieve admins: {error_msg}")

    @bp.put("/<admin_id>")
    @bp.patch("/<admin_id>")
    def update_admin(admin_id: str):
        """
        Update admin information.
        
        Args:
            admin_id: Admin ID
            
        Request Body (all optional):
            - fullname: str
            - email: str (validated with regex)
            - phone: str (validated with regex)
            
        Returns:
            200 OK with updated admin data, or 404 if not found
        """
        data = request.get_json(silent=True) or {}

        try:
            # Input validation (format, required fields, regex) - handled by Pydantic
            req = AdminUpdateRequest.model_validate(data)
        except ValidationError as e:
            # Validation errors translated to HTTP responses
            raise AppError(e.errors())

        # Delegate to Business Logic Layer
        # Service handles: existence check, business rules, orchestrates repository calls
        updated_admin = svc.update_admin(
            admin_id, 
            req.fullname, 
            req.email, 
            req.phone
        )
        res = AdminResponse(
            id=updated_admin.id,
            fullname=updated_admin.fullname,
            email=updated_admin.email,
            phone=updated_admin.phone
        )

        return api_response(HTTPStatus.OK, {
            "success": True,
            **res.model_dump()
        })

    return bp
