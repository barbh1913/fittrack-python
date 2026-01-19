from flask import Blueprint, request
from http import HTTPStatus
from pydantic import ValidationError

from backend.app.services.checkin_service import CheckinService
from backend.app.exceptions.exceptions import AppError, NotFoundError
from backend.app.schemas.checkin_schema import CheckinRequest, CheckinResponse
from backend.app.utils.response import api_response
import logging

logger = logging.getLogger(__name__)


def create_checkin_blueprint(db_manager):
    """
    Interface Layer: Handles HTTP requests/responses, delegates to Business Logic Layer.
    """
    bp = Blueprint("checkin", __name__, url_prefix="/api/checkin")
    # Use Service Layer (Business Logic) instead of Repository (Data Access)
    svc = CheckinService(db_manager)

    @bp.post("")
    def do_checkin():
        data = request.get_json(silent=True) or {}

        try:
            # Input validation (format, required fields) - handled by Pydantic
            req = CheckinRequest.model_validate(data)
        except ValidationError as e:
            # Validation errors translated to HTTP responses
            raise AppError(e.errors())

        try:
            # Delegate to Business Logic Layer
            # Service handles: all business rules (subscription status, limits, debt, etc.)
            c = svc.process_checkin(req.member_id)
            
            if c is None or c is False:
                raise AppError("Check-in failed. Unable to process check-in request.")

            # Access attributes safely - extract values immediately
            # The repository expunges the object, but we access attributes here to be safe
            from backend.app.models.enums import CheckinResult
            
            # Safely get result value (handle both enum and string)
            try:
                result_value = getattr(c, 'result', None)
                if result_value is None:
                    result_value = CheckinResult.DENIED.value
                elif isinstance(result_value, CheckinResult):
                    result_value = result_value.value
                elif result_value not in [e.value for e in CheckinResult]:
                    # If somehow we got an invalid value, default to DENIED
                    result_value = CheckinResult.DENIED.value
            except Exception as attr_e:
                logger.error(f"Error accessing result attribute: {str(attr_e)}")
                result_value = CheckinResult.DENIED.value

            # Safely get reason value (ensure it's a string)
            try:
                reason_value = getattr(c, 'reason', None)
                if reason_value is None:
                    reason_value = ""
                else:
                    reason_value = str(reason_value)
            except Exception as attr_e:
                logger.error(f"Error accessing reason attribute: {str(attr_e)}")
                reason_value = ""
            
            # Ensure reason is provided for denied check-ins
            if result_value == CheckinResult.DENIED.value and not reason_value:
                reason_value = "Check-in denied. Please contact administration for details."

            res = CheckinResponse(result=result_value, reason=reason_value)

            return api_response(HTTPStatus.CREATED, {
                "success": True,
                **res.model_dump()
            })
        except (AppError, NotFoundError) as e:
            # Re-raise custom exceptions so they're handled by error handlers
            logger.warning(f"Check-in business error: {str(e)}")
            raise
        except Exception as e:
            # Catch any unexpected errors and return a proper JSON response
            logger.error(f"Unexpected error in check-in endpoint: {str(e)}", exc_info=True)
            # Return a denied check-in response for any unexpected errors
            # This ensures we always return JSON, not HTML
            try:
                res = CheckinResponse(
                    result="DENIED",
                    reason=f"System error: {str(e)}"
                )
                return api_response(HTTPStatus.INTERNAL_SERVER_ERROR, {
                    "success": False,
                    **res.model_dump()
                })
            except Exception as inner_e:
                # If even creating the response fails, return minimal JSON
                logger.error(f"Failed to create error response: {str(inner_e)}", exc_info=True)
                from flask import jsonify
                return jsonify({
                    "success": False,
                    "result": "DENIED",
                    "reason": "System error occurred"
                }), HTTPStatus.INTERNAL_SERVER_ERROR.value

    return bp
