"""
Flask Blueprint for Trainer API endpoints.
Implements: Create trainer, Get trainer by id, Update trainer, List all trainers.

This module demonstrates:
- Layer separation: API layer only handles HTTP requests/responses
- Business logic is delegated to Services layer
- Data access is handled by dbhandlers
"""
from flask import Blueprint, request
from http import HTTPStatus
from pydantic import ValidationError
import logging

from backend.app.services.trainer_service import TrainerService
from backend.app.exceptions.exceptions import AppError, NotFoundError
from backend.app.schemas.trainer_schema import TrainerCreateRequest, TrainerUpdateRequest, TrainerResponse
from backend.app.utils.response import api_response

logger = logging.getLogger(__name__)


def create_trainers_blueprint(db_manager):
    """
    Interface Layer: Handles HTTP requests/responses, delegates to Business Logic Layer.
    
    Args:
        db_manager: SQLManger instance for database access
        
    Returns:
        Blueprint: Configured Flask Blueprint
    """
    bp = Blueprint("trainers", __name__, url_prefix="/api/trainers")
    # Use Service Layer (Business Logic) instead of Repository (Data Access)
    svc = TrainerService(db_manager)

    @bp.post("")
    def create_trainer():
        """
        Create a new trainer.
        
        Request Body:
            - id: str (alphanumeric, max 15 chars)
            - fullname: str
            - email: str (validated with regex)
            - phone: str (validated with regex)
            
        Returns:
            201 Created with trainer data
        """
        data = request.get_json(silent=True) or {}

        try:
            # Input validation (format, required fields, regex) - handled by Pydantic
            req = TrainerCreateRequest.model_validate(data)
        except ValidationError as e:
            # Validation errors translated to HTTP responses
            raise AppError(e.errors())

        # Delegate to Business Logic Layer
        # Service handles: uniqueness check, business rules, orchestrates repository calls
        trainer = svc.create_trainer(req.id, req.fullname, req.email, req.phone)

        res = TrainerResponse(
            id=trainer.id,
            fullname=trainer.fullname,
            email=trainer.email,
            phone=trainer.phone
        )

        return api_response(HTTPStatus.CREATED, {
            "success": True,
            **res.model_dump()
        })

    @bp.get("/<trainer_id>")
    def get_trainer(trainer_id: str):
        """
        Get trainer by ID.
        
        Args:
            trainer_id: Trainer ID
            
        Returns:
            200 OK with trainer data, or 404 if not found
        """
        try:
            # Delegate to Business Logic Layer
            trainer = svc.get_trainer(trainer_id)

            res = TrainerResponse(
                id=trainer.id,
                fullname=trainer.fullname,
                email=trainer.email,
                phone=trainer.phone
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
            
            logger.error(f"Error in get_trainer: {error_type}: {error_msg}", exc_info=True)
            
            if "doesn't exist" in error_msg.lower() or "Table" in error_type:
                raise AppError("Database tables not found. Please run 'python seed.py' to create tables and load data.")
            else:
                raise AppError(f"Database error: {error_msg}")

    @bp.get("")
    def list_trainers():
        """
        Get all trainers.
        
        Returns:
            200 OK with list of all trainers
        """
        try:
            trainers = svc.get_all_trainers()
            trainers_list = [
                TrainerResponse(
                    id=t.id,
                    fullname=t.fullname,
                    email=t.email,
                    phone=t.phone
                ).model_dump()
                for t in trainers
            ]
            
            return api_response(HTTPStatus.OK, {
                "success": True,
                "trainers": trainers_list,
                "count": len(trainers_list)
            })
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in list_trainers: {error_msg}", exc_info=True)
            raise AppError(f"Failed to retrieve trainers: {error_msg}")

    @bp.put("/<trainer_id>")
    @bp.patch("/<trainer_id>")
    def update_trainer(trainer_id: str):
        """
        Update trainer information.
        
        Args:
            trainer_id: Trainer ID
            
        Request Body (all optional):
            - fullname: str
            - email: str (validated with regex)
            - phone: str (validated with regex)
            
        Returns:
            200 OK with updated trainer data, or 404 if not found
        """
        data = request.get_json(silent=True) or {}

        try:
            # Input validation (format, required fields, regex) - handled by Pydantic
            req = TrainerUpdateRequest.model_validate(data)
        except ValidationError as e:
            # Validation errors translated to HTTP responses
            raise AppError(e.errors())

        # Delegate to Business Logic Layer
        # Service handles: existence check, business rules, orchestrates repository calls
        updated_trainer = svc.update_trainer(
            trainer_id, 
            req.fullname, 
            req.email, 
            req.phone
        )
        res = TrainerResponse(
            id=updated_trainer.id,
            fullname=updated_trainer.fullname,
            email=updated_trainer.email,
            phone=updated_trainer.phone
        )

        return api_response(HTTPStatus.OK, {
            "success": True,
            **res.model_dump()
        })

    return bp
