from flask import Blueprint, request
from http import HTTPStatus
from pydantic import ValidationError

from backend.app.schemas.class_session_schema import (
    ClassSessionCreate,
    ClassSessionCreateResponse,
    EnrollmentCreateRequest,
    EnrollmentCreateResponse,
    EnrollmentCancelRequest,
    ParticipantResponse,
)
from backend.app.services.class_session_service import ClassSessionService
from backend.app.models.enums import SessionStatus
from backend.app.exceptions.exceptions import AppError, NotFoundError, DuplicateError
from backend.app.utils.response import api_response


def create_sessions_blueprint(db_manager):
    """
    Interface Layer: Handles HTTP requests/responses, delegates to Business Logic Layer.
    """
    bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")
    # Use Service Layer (Business Logic) instead of Repository (Data Access)
    svc = ClassSessionService(db_manager)

    @bp.post("")
    def create_session():
        data = request.get_json(silent=True) or {}

        try:
            req = ClassSessionCreate.model_validate(data)
        except ValidationError as e:
            raise AppError(e.errors())

        from backend.app.models.enums import SessionStatus
        # Convert string to enum, or use default
        status_enum = SessionStatus(req.status) if req.status else SessionStatus.OPEN
        s = svc.create_session(req.title, req.starts_at, int(req.capacity), req.trainer_id, status_enum)
        res = ClassSessionCreateResponse(session_id=s.id)
        return api_response(HTTPStatus.CREATED, {"success": True, **res.model_dump()})

    @bp.post("/<session_id>/enroll")
    def enroll(session_id):
        data = request.get_json(silent=True) or {}

        try:
            req = EnrollmentCreateRequest.model_validate(data)
        except ValidationError as e:
            raise AppError(e.errors())

        try:
            e = svc.enroll_member(session_id, req.member_id)
            
            # Safely access enrollment ID (object might be expunged)
            enrollment_id = getattr(e, 'id', None)
            if enrollment_id is None:
                raise AppError("Enrollment created but ID not available")
            
            res = EnrollmentCreateResponse(enrollment_id=enrollment_id)
            return api_response(HTTPStatus.CREATED, {"success": True, **res.model_dump()})
        except (NotFoundError, DuplicateError, AppError):
            # Re-raise custom exceptions so they're handled by error handlers
            raise
        except Exception as e:
            import logging
            logging.error(f"Unexpected error in enroll endpoint: {str(e)}", exc_info=True)
            raise AppError(f"Failed to enroll member: {str(e)}")

    @bp.post("/<session_id>/cancel")
    def cancel(session_id):
        data = request.get_json(silent=True) or {}

        try:
            req = EnrollmentCancelRequest.model_validate(data)
        except ValidationError as e:
            raise AppError(e.errors())

        try:
            result = svc.cancel_enrollment(session_id, req.member_id, req.cancel_reason)
            # Verify cancellation was successful
            if result is False or result is None:
                raise AppError("Failed to cancel enrollment")
            return api_response(HTTPStatus.OK, {"success": True, "message": "Enrollment canceled successfully"})
        except (NotFoundError, AppError):
            # Re-raise custom exceptions so they're handled by error handlers
            raise
        except Exception as e:
            import logging
            logging.error(f"Unexpected error in cancel endpoint: {str(e)}", exc_info=True)
            raise AppError(f"Failed to cancel enrollment: {str(e)}")

    @bp.get("/<session_id>/participants")
    def participants(session_id):
        res = svc.list_participants(session_id)
        participants_out = [ParticipantResponse.model_validate(p).model_dump() for p in res]
        return api_response(HTTPStatus.OK, {"success": True, "participants": participants_out})

    @bp.get("/weekly")
    def get_weekly_sessions():
        """Get all sessions for the current week with participant counts."""
        member_id = request.args.get('member_id')
        sessions = svc.get_weekly_sessions(member_id)
        return api_response(HTTPStatus.OK, {"success": True, "sessions": sessions})

    @bp.get("/trainer/<trainer_id>")
    def get_trainer_sessions(trainer_id):
        """Get all sessions for a specific trainer."""
        sessions = svc.get_trainer_sessions(trainer_id)
        return api_response(HTTPStatus.OK, {"success": True, "sessions": sessions})

    @bp.get("")
    def list_sessions():
        """Get all sessions with trainer info and participant counts."""
        sessions = svc.get_all_sessions()
        return api_response(HTTPStatus.OK, {"success": True, "sessions": sessions, "count": len(sessions)})

    return bp
