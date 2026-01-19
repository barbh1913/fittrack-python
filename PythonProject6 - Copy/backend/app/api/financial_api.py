"""
Flask Blueprint for Financial Reports API endpoints.
Implements revenue, debt, and demand reporting.
"""
from flask import Blueprint, request
from http import HTTPStatus
from datetime import datetime, timedelta
import logging

from backend.app.services.financial_service import FinancialService
from backend.app.exceptions.exceptions import AppError
from backend.app.utils.response import api_response

logger = logging.getLogger(__name__)


def create_financial_blueprint(db_manager):
    """
    Interface Layer: Handles HTTP requests/responses, delegates to Business Logic Layer.
    
    Args:
        db_manager: SQLManger instance for database access
        
    Returns:
        Blueprint: Configured Flask Blueprint
    """
    bp = Blueprint("financial", __name__, url_prefix="/api/financial")
    # Use Service Layer (Business Logic) instead of Repository (Data Access)
    svc = FinancialService(db_manager)

    @bp.get("/revenue")
    def get_revenue_report():
        """
        Get revenue report by month or subscription type.
        
        Query Params:
            - start_date: ISO date string (optional)
            - end_date: ISO date string (optional)
            - group_by: "month" or "plan_type" (default: "month")
        
        Returns:
            200 OK with revenue breakdown
        """
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        group_by = request.args.get('group_by', 'month')

        try:
            # Parse dates if provided
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None
            
            # Delegate to Business Logic Layer
            result = svc.get_revenue_report(start_dt, end_dt, group_by)
            
            return api_response(HTTPStatus.OK, {
                "success": True,
                **result
            })
        except Exception as e:
            logger.error(f"Error getting revenue report: {str(e)}", exc_info=True)
            raise AppError(f"Failed to get revenue report: {str(e)}")

    @bp.get("/debts")
    def get_debts_report():
        """
        Get open debts report.
        
        Returns:
            200 OK with list of members with outstanding debts
        """
        try:
            # Delegate to Business Logic Layer
            result = svc.get_debts_report()
            
            return api_response(HTTPStatus.OK, {
                "success": True,
                **result
            })
        except Exception as e:
            logger.error(f"Error getting debts report: {str(e)}", exc_info=True)
            raise AppError(f"Failed to get debts report: {str(e)}")

    @bp.get("/demand-metrics")
    def get_demand_metrics():
        """
        Get demand metrics for classes (profitable/overloaded).
        
        Returns:
            200 OK with class demand statistics
        """
        try:
            # Delegate to Business Logic Layer
            result = svc.get_demand_metrics()
            
            return api_response(HTTPStatus.OK, {
                "success": True,
                **result
            })
        except Exception as e:
            logger.error(f"Error getting demand metrics: {str(e)}", exc_info=True)
            raise AppError(f"Failed to get demand metrics: {str(e)}")

    @bp.get("/high-demand")
    def get_high_demand_sessions():
        """
        Get high-demand sessions with recommendations.
        
        Query Params:
            - min_waiting: int (default: 5)
            - min_waiting_hours: int (default: 24)
        
        Returns:
            200 OK with high-demand sessions and recommendations
        """
        min_waiting = int(request.args.get('min_waiting', 5))
        min_waiting_hours = int(request.args.get('min_waiting_hours', 24))

        try:
            # Delegate to Business Logic Layer
            high_demand = svc.get_high_demand_sessions(min_waiting, min_waiting_hours)
            
            return api_response(HTTPStatus.OK, {
                "success": True,
                "high_demand_sessions": high_demand,
                "count": len(high_demand)
            })
        except Exception as e:
            logger.error(f"Error getting high-demand sessions: {str(e)}", exc_info=True)
            raise AppError(f"Failed to get high-demand sessions: {str(e)}")

    return bp
