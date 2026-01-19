from flask import Blueprint, request
from http import HTTPStatus
from pydantic import ValidationError

from backend.app.services.workout_plan_service import WorkoutPlanService
from backend.app.exceptions.exceptions import AppError, NotFoundError
from backend.app.schemas.workout_plan_schema import (
    WorkoutPlanCreateRequest,
    WorkoutPlanCreateResponse,
)
from backend.app.utils.response import api_response


def create_workout_plans_blueprint(db_manager):
    """
    Interface Layer: Handles HTTP requests/responses, delegates to Business Logic Layer.
    """
    bp = Blueprint("workout_plans", __name__, url_prefix="/api/workout-plans")
    # Use Service Layer (Business Logic) instead of Repository (Data Access)
    svc = WorkoutPlanService(db_manager)

    @bp.post("")
    def create_plan():
        data = request.get_json(silent=True) or {}

        try:
            # Input validation (format, required fields) - handled by Pydantic
            req = WorkoutPlanCreateRequest.model_validate(data)
        except ValidationError as e:
            # Validation errors translated to HTTP responses
            raise AppError(e.errors())

        try:
            # Delegate to Business Logic Layer
            # Service handles: trainer/member validation, business rules
            wp = svc.create_workout_plan(req.trainer_id, req.member_id, req.title, req.items)
        except NotFoundError as e:
            raise
        except Exception as e:
            import logging
            logging.error(f"Error creating workout plan: {str(e)}", exc_info=True)
            raise AppError(f"Failed to create workout plan: {str(e)}")

        res = WorkoutPlanCreateResponse(workout_plan_id=wp.id)
        return api_response(HTTPStatus.CREATED, {"success": True, **res.model_dump()})

    @bp.get("/members/<member_id>/<workout_plan_id>")
    def view_plan(member_id, workout_plan_id):
        """Get full workout plan with all items for a member."""
        result = svc.get_workout_plan_for_member(member_id, workout_plan_id)
        
        plan = result["plan"]
        items = result["items"]
        
        # Return full structured data
        return api_response(HTTPStatus.OK, {
            "success": True,
            "plan": {
                "id": plan.id,
                "title": plan.title,
                "trainer_id": plan.trainer_id,
                "member_id": plan.member_id,
                "created_at": plan.created_at.isoformat() if plan.created_at else None,
                "is_active": plan.is_active
            },
            "items": [
                {
                    "id": item.id,
                    "exercise_name": item.exercise_name,
                    "sets": item.sets,
                    "reps": item.reps,
                    "target_weight": item.target_weight,
                    "notes": item.notes
                }
                for item in items
            ]
        })

    @bp.get("/members/<member_id>")
    def get_member_plans(member_id):
        """Get all workout plans for a member with trainer info and sample exercises."""
        plans = svc.get_all_workout_plans_for_member(member_id)
        return api_response(HTTPStatus.OK, {"success": True, "plans": plans})

    return bp
