"""
Business Logic Layer for Financial operations.
This service contains all business rules for financial reporting.
It orchestrates database operations through the repository layer.
"""
from datetime import datetime
from backend.app.repositories.waiting_list import db_waiting_list
from backend.app.models.Subscription import Subscription
from backend.app.models.Payment import Payment
from backend.app.models.Plan import Plan
from backend.app.models.ClassSession import ClassSession
from backend.app.models.Enrollment import Enrollment
from backend.app.models.enums import PaymentStatus, SubscriptionStatus, EnrollmentStatus
from backend.app.exceptions.exceptions import AppError
import logging

logger = logging.getLogger(__name__)


class FinancialService:
    """
    Service class for financial reporting business logic.
    Handles all business rules for revenue, debt, and demand reporting.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the service with database manager.
        
        Args:
            db_manager: SQLManger instance for database access
        """
        self.SessionLocal = db_manager.SessionLocal
        self.db_manager = db_manager
    
    def get_revenue_report(self, start_date: datetime = None, end_date: datetime = None, group_by: str = 'month'):
        """
        Get revenue report with business logic.
        
        Business Rules:
        - Only PAID payments are included
        - Can group by month or plan type
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            group_by: 'month' or 'plan_type'
            
        Returns:
            dict: Revenue breakdown
        """
        with self.SessionLocal() as session:
            try:
                # Build query
                query = (
                    session.query(Payment, Subscription, Plan)
                    .join(Subscription, Subscription.id == Payment.subscription_id)
                    .join(Plan, Plan.id == Subscription.plan_id)
                    .filter(Payment.status == PaymentStatus.PAID.value)
                )

                if start_date:
                    query = query.filter(Payment.paid_at >= start_date)
                if end_date:
                    query = query.filter(Payment.paid_at <= end_date)

                payments = query.all()

                if group_by == "month":
                    # Group by month
                    revenue_by_month = {}
                    for payment, sub, plan in payments:
                        if payment.paid_at:
                            month_key = payment.paid_at.strftime("%Y-%m")
                            if month_key not in revenue_by_month:
                                revenue_by_month[month_key] = 0
                            revenue_by_month[month_key] += payment.amount

                    return {
                        "revenue_by_month": revenue_by_month,
                        "total_revenue": sum(revenue_by_month.values())
                    }
                else:
                    # Group by plan type
                    revenue_by_type = {}
                    for payment, sub, plan in payments:
                        plan_type = plan.plan_type
                        if plan_type not in revenue_by_type:
                            revenue_by_type[plan_type] = 0
                        revenue_by_type[plan_type] += payment.amount

                    return {
                        "revenue_by_plan_type": revenue_by_type,
                        "total_revenue": sum(revenue_by_type.values())
                    }

            except Exception as e:
                logger.error(f"Error getting revenue report: {str(e)}", exc_info=True)
                raise AppError(f"Failed to get revenue report: {str(e)}")
    
    def get_debts_report(self):
        """
        Get open debts report.
        
        Business Rules:
        - Only subscriptions with outstanding_debt > 0
        
        Returns:
            dict: Debts data
        """
        with self.SessionLocal() as session:
            try:
                from backend.app.models.Member import Member
                
                subscriptions_with_debt = (
                    session.query(Subscription, Member)
                    .join(Member, Member.id == Subscription.member_id)
                    .filter(Subscription.outstanding_debt > 0)
                    .all()
                )

                debts = [
                    {
                        "member_id": m.id,
                        "member_name": m.fullname,
                        "subscription_id": sub.id,
                        "outstanding_debt": sub.outstanding_debt,
                        "status": sub.status
                    }
                    for sub, m in subscriptions_with_debt
                ]

                total_debt = sum(d["outstanding_debt"] for d in debts)

                return {
                    "debts": debts,
                    "count": len(debts),
                    "total_debt": total_debt
                }

            except Exception as e:
                logger.error(f"Error getting debts report: {str(e)}", exc_info=True)
                raise AppError(f"Failed to get debts report: {str(e)}")
    
    def get_demand_metrics(self):
        """
        Get demand metrics for classes.
        
        Business Rules:
        - Calculate utilization percentage
        - Identify overloaded (waiting > 5) and profitable (utilization > 80%) classes
        
        Returns:
            dict: Demand metrics
        """
        with self.SessionLocal() as session:
            try:
                # Get all sessions with enrollment counts
                sessions = session.query(ClassSession).all()

                metrics = []
                waiting_list_repo = db_waiting_list(self.db_manager)
                
                for cs in sessions:
                    enrollment_count = (
                        session.query(Enrollment)
                        .filter(
                            Enrollment.class_session_id == cs.id,
                            Enrollment.status == EnrollmentStatus.REGISTERED.value
                        )
                        .count()
                    )

                    # Get waiting list count
                    waiting_entries = waiting_list_repo.get_waiting_list(cs.id)
                    waiting_count = len([e for e in waiting_entries if e["status"] == "WAITING"])

                    utilization = (enrollment_count / cs.capacity * 100) if cs.capacity > 0 else 0

                    metrics.append({
                        "session_id": cs.id,
                        "session_title": cs.title,
                        "capacity": cs.capacity,
                        "enrolled": enrollment_count,
                        "waiting": waiting_count,
                        "utilization_percent": round(utilization, 2),
                        "is_overloaded": waiting_count > 5,
                        "is_profitable": utilization > 80
                    })

                return {
                    "metrics": metrics,
                    "count": len(metrics)
                }

            except Exception as e:
                logger.error(f"Error getting demand metrics: {str(e)}", exc_info=True)
                raise AppError(f"Failed to get demand metrics: {str(e)}")
    
    def get_high_demand_sessions(self, min_waiting: int = 5, min_waiting_hours: int = 24):
        """
        Get high-demand sessions with recommendations.
        
        Business Rules:
        - Sessions with > min_waiting waiting members
        - Or > min_waiting waiting for > min_waiting_hours
        
        Args:
            min_waiting: Minimum waiting count threshold
            min_waiting_hours: Minimum waiting hours threshold
            
        Returns:
            list: High-demand sessions
        """
        try:
            waiting_list_repo = db_waiting_list(self.db_manager)
            high_demand = waiting_list_repo.detect_high_demand(min_waiting, min_waiting_hours)
            return high_demand
        except Exception as e:
            logger.error(f"Error getting high-demand sessions: {str(e)}", exc_info=True)
            raise AppError(f"Failed to get high-demand sessions: {str(e)}")
