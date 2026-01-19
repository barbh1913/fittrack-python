"""
Flask Blueprint for Member API endpoints.
Implements: Create member, Get member by id, Update member.

This module demonstrates:
- Layer separation: API layer only handles HTTP requests/responses
- Business logic is delegated to Services layer
- Data access is handled by dbhandlers
"""
from flask import Blueprint, request
from http import HTTPStatus
from pydantic import ValidationError
import logging

from backend.app.services.member_service import MemberService
from backend.app.exceptions.exceptions import AppError, NotFoundError, DuplicateError
from backend.app.schemas.member_schema import MemberCreateRequest, MemberUpdateRequest, MemberResponse
from backend.app.utils.response import api_response

logger = logging.getLogger(__name__)


def create_members_blueprint(db_manager):
    """
    Create and configure the members blueprint.
    
    Interface Layer: Handles HTTP requests/responses, delegates to Business Logic Layer.
    
    Args:
        db_manager: SQLManger instance for database access
        
    Returns:
        Blueprint: Configured Flask Blueprint
    """
    bp = Blueprint("members", __name__, url_prefix="/api/members")
    # Use Service Layer (Business Logic) instead of Repository (Data Access)
    svc = MemberService(db_manager)

    @bp.post("")
    def create_member():
        """
        Create a new member.
        
        Request Body:
            - id: str (9 digits)
            - fullname: str
            - email: str (validated with regex)
            - phone: str (validated with regex)
            
        Returns:
            201 Created with member data
        """
        data = request.get_json(silent=True) or {}

        try:
            # Input validation (format, required fields, regex) - handled by Pydantic
            req = MemberCreateRequest.model_validate(data)
        except ValidationError as e:
            # Validation errors translated to HTTP responses
            raise AppError(e.errors())

        try:
            # Delegate to Business Logic Layer (Service)
            # Service handles: uniqueness check, business rules, orchestrates repository calls
            member = svc.create_member(req.id, req.fullname, req.email, req.phone)

            # Safely access member attributes
            res = MemberResponse(
                id=getattr(member, 'id', req.id),
                fullname=getattr(member, 'fullname', req.fullname),
                email=getattr(member, 'email', req.email),
                phone=getattr(member, 'phone', req.phone)
            )

            return api_response(HTTPStatus.CREATED, {
                "success": True,
                **res.model_dump()
            })
        except (DuplicateError, AppError, NotFoundError):
            # Re-raise custom exceptions so they're handled by error handlers
            raise
        except Exception as e:
            # Catch any unexpected errors
            logger.error(f"Unexpected error in create_member: {str(e)}", exc_info=True)
            raise AppError(f"Failed to create member: {str(e)}")

    @bp.get("/<member_id>")
    def get_member(member_id: str):
        """
        Get member by ID.
        
        Args:
            member_id: Member ID (9 digits)
            
        Returns:
            200 OK with member data, or 404 if not found
        """
        try:
            # Delegate to Business Logic Layer
            member = svc.get_member(member_id)

            res = MemberResponse(
                id=member.id,
                fullname=member.fullname,
                email=member.email,
                phone=member.phone
            )

            return api_response(HTTPStatus.OK, {
                "success": True,
                **res.model_dump()
            })
        except (NotFoundError, AppError):
            # Re-raise custom exceptions so they're handled by error handlers
            raise
        except Exception as e:
            # Catch any other exceptions (database errors, etc.)
            error_msg = str(e)
            error_type = type(e).__name__
            
            logger.error(f"Error in get_member: {error_type}: {error_msg}", exc_info=True)
            
            # Check if it's a table doesn't exist error
            if "doesn't exist" in error_msg.lower() or "Table" in error_type:
                raise AppError("Database tables not found. Please run 'python seed.py' to create tables and load data.")
            else:
                raise AppError(f"Database error: {error_msg}")

    @bp.get("")
    def list_members():
        """
        Get all members.
        
        Returns:
            200 OK with list of all members
        """
        try:
            # Delegate to Business Logic Layer
            members = svc.get_all_members()
            members_list = [
                MemberResponse(
                    id=m.id,
                    fullname=m.fullname,
                    email=m.email,
                    phone=m.phone
                ).model_dump()
                for m in members
            ]
            
            return api_response(HTTPStatus.OK, {
                "success": True,
                "members": members_list,
                "count": len(members_list)
            })
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in list_members: {error_msg}", exc_info=True)
            raise AppError(f"Failed to retrieve members: {error_msg}")

    @bp.put("/<member_id>")
    @bp.patch("/<member_id>")
    def update_member(member_id: str):
        """
        Update member information.
        
        Args:
            member_id: Member ID (9 digits)
            
        Request Body (all optional):
            - fullname: str
            - email: str (validated with regex)
            - phone: str (validated with regex)
            
        Returns:
            200 OK with updated member data, or 404 if not found
        """
        data = request.get_json(silent=True) or {}

        try:
            # Input validation (format, required fields, regex) - handled by Pydantic
            req = MemberUpdateRequest.model_validate(data)
        except ValidationError as e:
            # Validation errors translated to HTTP responses
            raise AppError(e.errors())

        try:
            # Delegate to Business Logic Layer
            # Service handles: existence check, business rules, orchestrates repository calls
            updated_member = svc.update_member(
                member_id, 
                req.fullname, 
                req.email, 
                req.phone
            )
            
            # Safely access member attributes
            res = MemberResponse(
                id=getattr(updated_member, 'id', member_id),
                fullname=getattr(updated_member, 'fullname', req.fullname or ''),
                email=getattr(updated_member, 'email', req.email or ''),
                phone=getattr(updated_member, 'phone', req.phone or '')
            )

            return api_response(HTTPStatus.OK, {
                "success": True,
                **res.model_dump()
            })
        except (NotFoundError, AppError):
            # Re-raise custom exceptions so they're handled by error handlers
            raise
        except Exception as e:
            # Catch any unexpected errors
            logger.error(f"Unexpected error in update_member: {str(e)}", exc_info=True)
            raise AppError(f"Failed to update member: {str(e)}")

    return bp
