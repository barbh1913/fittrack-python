"""
Flask Blueprint for Progress Tracking API endpoints.
Implements workout progress logging and history.
"""
from flask import Blueprint, request
from http import HTTPStatus
from pydantic import ValidationError, BaseModel, Field
import logging

from backend.app.services.progress_service import ProgressService
from backend.app.exceptions.exceptions import AppError, NotFoundError
from backend.app.utils.response import api_response

logger = logging.getLogger(__name__)


class ProgressLogRequest(BaseModel):
    """Request schema for logging progress."""
    workout_plan_id: str = Field(..., max_length=15)
    workout_item_id: str = Field(..., max_length=15)
    sets_completed: int = Field(..., ge=0)
    reps_completed: int = Field(..., ge=0)
    weight_used: float = Field(None, ge=0)
    duration_minutes: int = Field(None, ge=0)
    notes: str = Field(None, max_length=500)


def create_progress_blueprint(db_manager):
    """
    Interface Layer: Handles HTTP requests/responses, delegates to Business Logic Layer.
    
    Args:
        db_manager: SQLManger instance for database access
        
    Returns:
        Blueprint: Configured Flask Blueprint
    """
    bp = Blueprint("progress", __name__, url_prefix="/api/progress")
    # Use Service Layer (Business Logic) instead of Repository (Data Access)
    svc = ProgressService(db_manager)

    @bp.post("/log")
    def log_progress():
        """
        Log workout progress for a specific exercise.
        
        Request Body:
            - workout_plan_id: str
            - workout_item_id: str
            - sets_completed: int (>= 0)
            - reps_completed: int (>= 0)
            - weight_used: float (optional, >= 0)
            - duration_minutes: int (optional, >= 0)
            - notes: str (optional)
        
        Returns:
            201 Created with progress log details
        """
        data = request.get_json(silent=True) or {}

        try:
            req = ProgressLogRequest.model_validate(data)
        except ValidationError as e:
            raise AppError(e.errors())

        # Get member_id from auth context (would need to be implemented)
        # For now, assume it's in the request or use a placeholder
        member_id = data.get("member_id")
        if not member_id:
            raise AppError("member_id is required")

        try:
            log = svc.log_progress(
                req.workout_plan_id,
                req.workout_item_id,
                member_id,
                req.sets_completed,
                req.reps_completed,
                req.weight_used,
                req.duration_minutes,
                req.notes
            )
            return api_response(HTTPStatus.CREATED, {
                "success": True,
                "progress_log_id": log.id,
                "message": "Progress logged successfully"
            })
        except (NotFoundError, AppError) as e:
            raise
        except Exception as e:
            logger.error(f"Error logging progress: {str(e)}", exc_info=True)
            raise AppError(f"Failed to log progress: {str(e)}")

    @bp.get("/history/<workout_plan_id>")
    def get_progress_history(workout_plan_id: str):
        """
        Get progress history for a workout plan.
        
        Query Params:
            - member_id: str (required)
            - limit: int (default: 50)
        
        Returns:
            200 OK with progress history
        """
        member_id = request.args.get('member_id')
        limit = int(request.args.get('limit', 50))

        if not member_id:
            raise AppError("member_id is required")

        try:
            history = svc.get_progress_history(workout_plan_id, member_id, limit)
            return api_response(HTTPStatus.OK, {
                "success": True,
                "history": history,
                "count": len(history)
            })
        except (NotFoundError, AppError) as e:
            raise
        except Exception as e:
            logger.error(f"Error getting progress history: {str(e)}", exc_info=True)
            raise AppError(f"Failed to get progress history: {str(e)}")

    @bp.get("/trainer-summary")
    def get_trainer_progress_summary():
        """
        Get progress summary for all trainees of a trainer.
        
        Query Params:
            - trainer_id: str (required)
        
        Returns:
            200 OK with trainee progress summaries
        """
        trainer_id = request.args.get('trainer_id')
        if not trainer_id:
            raise AppError("trainer_id is required")

        try:
            summaries = svc.get_trainee_progress_summary(trainer_id)
            return api_response(HTTPStatus.OK, {
                "success": True,
                "summaries": summaries,
                "count": len(summaries)
            })
        except Exception as e:
            logger.error(f"Error getting trainer progress summary: {str(e)}", exc_info=True)
            raise AppError(f"Failed to get trainer progress summary: {str(e)}")

    @bp.get("/member-summary/<member_id>")
    def get_member_progress_summary(member_id: str):
        """
        Get progress summary for a member across all their workout plans.
        
        Returns:
            200 OK with member progress summaries
        """
        try:
            summaries = svc.get_member_progress_summary(member_id)
            return api_response(HTTPStatus.OK, {
                "success": True,
                "summaries": summaries,
                "count": len(summaries)
            })
        except Exception as e:
            logger.error(f"Error getting member progress summary: {str(e)}", exc_info=True)
            raise AppError(f"Failed to get member progress summary: {str(e)}")

    return bp
