"""
Flask Blueprint for Waiting List API endpoints.
Implements queue management operations.
"""
from flask import Blueprint, request
from http import HTTPStatus
from pydantic import ValidationError
import logging

from backend.app.services.waiting_list_service import WaitingListService
from backend.app.exceptions.exceptions import AppError, NotFoundError, DuplicateError
from backend.app.utils.response import api_response

logger = logging.getLogger(__name__)


def create_waiting_list_blueprint(db_manager):
    """
    Interface Layer: Handles HTTP requests/responses, delegates to Business Logic Layer.
    
    Args:
        db_manager: SQLManger instance for database access
        
    Returns:
        Blueprint: Configured Flask Blueprint
    """
    bp = Blueprint("waiting_list", __name__, url_prefix="/api/waiting-list")
    # Use Service Layer (Business Logic) instead of Repository (Data Access)
    svc = WaitingListService(db_manager)

    @bp.post("/sessions/<session_id>")
    def add_to_waiting_list(session_id: str):
        """
        Add a member to the waiting list for a full session.
        
        Request Body:
            - member_id: str
        
        Returns:
            201 Created with waiting list entry details
        """
        data = request.get_json(silent=True) or {}
        member_id = data.get("member_id")
        
        if not member_id:
            raise AppError("member_id is required")

        try:
            wl_entry = svc.add_to_waiting_list(session_id, member_id)
            return api_response(HTTPStatus.CREATED, {
                "success": True,
                "waiting_list_id": wl_entry.id,
                "position": wl_entry.position,
                "status": wl_entry.status,
                "message": f"You have been added to the waiting list at position {wl_entry.position}"
            })
        except (NotFoundError, DuplicateError, AppError) as e:
            raise
        except Exception as e:
            logger.error(f"Error adding to waiting list: {str(e)}", exc_info=True)
            raise AppError(f"Failed to add to waiting list: {str(e)}")

    @bp.post("/<waiting_list_id>/confirm")
    def confirm_assignment(waiting_list_id: str):
        """
        Confirm assignment and create enrollment.
        Called when member approves the spot.
        
        Returns:
            200 OK with enrollment details
        """
        try:
            enrollment = svc.confirm_assignment(waiting_list_id)
            return api_response(HTTPStatus.OK, {
                "success": True,
                "enrollment_id": enrollment.id,
                "message": "Assignment confirmed. You are now enrolled in the session."
            })
        except (NotFoundError, AppError) as e:
            raise
        except Exception as e:
            logger.error(f"Error confirming assignment: {str(e)}", exc_info=True)
            raise AppError(f"Failed to confirm assignment: {str(e)}")

    @bp.get("/sessions/<session_id>")
    def get_waiting_list(session_id: str):
        """
        Get full waiting list for a session.
        
        Returns:
            200 OK with waiting list entries
        """
        try:
            entries = svc.get_waiting_list(session_id)
            return api_response(HTTPStatus.OK, {
                "success": True,
                "waiting_list": entries,
                "count": len(entries)
            })
        except Exception as e:
            logger.error(f"Error getting waiting list: {str(e)}", exc_info=True)
            raise AppError(f"Failed to get waiting list: {str(e)}")

    @bp.get("/members/<member_id>")
    def get_member_waiting_lists(member_id: str):
        """
        Get all waiting list entries for a member.
        
        Returns:
            200 OK with member's waiting list entries
        """
        try:
            # This would need to be added to the repository
            # For now, return a placeholder
            return api_response(HTTPStatus.OK, {
                "success": True,
                "message": "Member waiting list entries",
                "member_id": member_id
            })
        except Exception as e:
            logger.error(f"Error getting member waiting lists: {str(e)}", exc_info=True)
            raise AppError(f"Failed to get member waiting lists: {str(e)}")

    @bp.post("/check-expired")
    def check_expired_assignments():
        """
        Check for expired assignments and promote next in queue.
        Should be called periodically.
        
        Query Params:
            - session_id (optional): Check specific session only
        
        Returns:
            200 OK with count of expired assignments
        """
        session_id = request.args.get('session_id')
        try:
            count = svc.check_expired_assignments(session_id)
            return api_response(HTTPStatus.OK, {
                "success": True,
                "expired_count": count,
                "message": f"Processed {count} expired assignments"
            })
        except Exception as e:
            logger.error(f"Error checking expired assignments: {str(e)}", exc_info=True)
            raise AppError(f"Failed to check expired assignments: {str(e)}")

    return bp
