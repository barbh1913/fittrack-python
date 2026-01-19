from flask import Blueprint, request
from http import HTTPStatus
from pydantic import ValidationError

from backend.app.schemas.subscription_schema import (
    SubscriptionAssign,
    SubscriptionAssignResponse,
    SubscriptionFreezeRequest,
    SubscriptionStatusResponse,
)
from backend.app.services.subscription_service import SubscriptionService
from backend.app.exceptions.exceptions import AppError
from backend.app.utils.response import api_response


def create_subscriptions_blueprint(db_manager):
    """
    Interface Layer: Handles HTTP requests/responses, delegates to Business Logic Layer.
    """
    bp = Blueprint("subscriptions", __name__, url_prefix="/api/subscriptions")
    # Use Service Layer (Business Logic) instead of Repository (Data Access)
    svc = SubscriptionService(db_manager)

    @bp.post("")
    def assign_subscription():
        data = request.get_json(silent=True) or {}

        try:
            req = SubscriptionAssign.model_validate(data)
        except ValidationError as e:
            raise AppError(e.errors())

        sub = svc.assign_subscription(req.member_id, req.plan_id, req.start_date)

        res = SubscriptionAssignResponse(subscription_id=sub.id)
        return api_response(HTTPStatus.CREATED, {"success": True, **res.model_dump()})

    @bp.post("/<subscription_id>/freeze")
    def freeze(subscription_id):
        data = request.get_json(silent=True) or {}

        try:
            req = SubscriptionFreezeRequest.model_validate(data)
        except ValidationError as e:
            raise AppError(e.errors())

        sub = svc.freeze_subscription(subscription_id, int(req.days))

        return api_response(HTTPStatus.OK, {
            "success": True,
            "frozen_until": sub.frozen_until.isoformat() if sub.frozen_until else None
        })

    @bp.post("/<subscription_id>/unfreeze")
    def unfreeze(subscription_id):
        sub = svc.unfreeze_subscription(subscription_id)
        return api_response(HTTPStatus.OK, {"success": True, "status": sub.status})

    @bp.get("/<subscription_id>/status")
    def status(subscription_id):
        st = svc.get_subscription_status(subscription_id)
        res = SubscriptionStatusResponse(status=st)
        return api_response(HTTPStatus.OK, {"success": True, **res.model_dump()})

    return bp
