"""
Business Logic Layer for Check-in operations.
This service contains all business rules for the smart check-in process.
It orchestrates database operations through the repository layer.
"""
from datetime import datetime, timedelta
import uuid

from backend.app.repositories.checkin import db_checkin as CheckinRepository
from backend.app.repositories.subscription import db_Subscription
from backend.app.repositories.member import db_member
from backend.app.models.Member import Member
from backend.app.models.Subscription import Subscription
from backend.app.models.Payment import Payment
from backend.app.models.Checkin import Checkin
from backend.app.models.enums import SubscriptionStatus, CheckinResult, PaymentStatus
from backend.app.exceptions.exceptions import NotFoundError, AppError
import logging

logger = logging.getLogger(__name__)

class CheckinService:
    """
    Service class for check-in business logic.
    Implements the smart check-in process with all business rules.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the service with database manager.
        
        Args:
            db_manager: SQLManger instance for database access
        """
        self.SessionLocal = db_manager.SessionLocal
        self.checkin_repo = CheckinRepository(db_manager)
        self.member_repo = db_member(db_manager)
        self.subscription_repo = db_Subscription(db_manager)
        self.db_manager = db_manager
    
    def process_checkin(self, member_id: str) -> Checkin:
        """
        Process check-in for a member with comprehensive business validation.
        
        Args:
            member_id: Member ID
            
        Returns:
            Checkin: Checkin object with result (APPROVED or DENIED) and reason
            
        Note:
            This method implements the complete smart check-in business logic.
            The order of checks is critical for proper business rule enforcement.
        """
        now = datetime.now()
        
        with self.SessionLocal() as session:
            try:
                # Business Rule 1: Member must exist
                member = self.member_repo.get_member_by_id(member_id)
                if member is None:
                    denied = self.checkin_repo.create_checkin(
                        member_id, CheckinResult.DENIED.value, "Member not found", now
                    )
                    return denied
                
                # Business Rule 2: Active subscription must exist
                # Note: Using session.query directly for complex business logic query
                # This is acceptable in Service layer for queries that span business rules
                sub = (
                    session.query(Subscription)
                    .filter(
                        Subscription.member_id == member_id,
                        Subscription.status == SubscriptionStatus.ACTIVE.value
                    )
                    .first()
                )
                if sub is None:
                    denied = self.checkin_repo.create_checkin(
                        member_id, CheckinResult.DENIED.value, "No active subscription", now
                    )
                    return denied
                
                # Business Rule 3: Subscription must be within valid date range
                if now < sub.start_date or now > sub.end_date:
                    denied = self.checkin_repo.create_checkin(
                        member_id, CheckinResult.DENIED.value, "Subscription expired or not yet started", now
                    )
                    return denied
                
                # Business Rule 4: Subscription must not be frozen
                if sub.frozen_until is not None and sub.frozen_until > now:
                    denied = self.checkin_repo.create_checkin(
                        member_id, CheckinResult.DENIED.value, "Subscription is frozen", now
                    )
                    return denied
                
                # Business Rule 5: Subscription must have remaining entries
                if sub.remaining_entries <= 0:
                    denied = self.checkin_repo.create_checkin(
                        member_id, CheckinResult.DENIED.value, "No remaining entries (punch card limit reached)", now
                    )
                    return denied
                
                # Business Rule 6: No outstanding debt
                if sub.outstanding_debt > 0:
                    denied = self.checkin_repo.create_checkin(
                        member_id, CheckinResult.DENIED.value, "Unpaid debt or pending payment", now
                    )
                    return denied
                
                # Business Rule 7: No failed payments
                # Note: Using session.query directly for business rule validation
                # This is acceptable in Service layer for complex business queries
                failed_payments = (
                    session.query(Payment)
                    .filter(
                        Payment.subscription_id == sub.id,
                        Payment.status == PaymentStatus.FAILED.value
                    )
                    .count()
                )
                if failed_payments > 0:
                    denied = self.checkin_repo.create_checkin(
                        member_id, CheckinResult.DENIED.value, 
                        "Unpaid debt or pending payment", now
                    )
                    return denied
                
                # Business Rule 8: Daily entry limit (max 3 entries per day)
                today_start = datetime(now.year, now.month, now.day)
                today_checkins = self.checkin_repo.count_checkins(
                    member_id, start_date=today_start, result=CheckinResult.APPROVED.value
                )
                if today_checkins >= 3:
                    denied = self.checkin_repo.create_checkin(
                        member_id, CheckinResult.DENIED.value, 
                        "Entry limits exceeded (daily/weekly)", now
                    )
                    return denied
                
                # Business Rule 9: Weekly entry limit (max 15 entries per week)
                week_start = now - timedelta(days=now.weekday())
                week_start = datetime(week_start.year, week_start.month, week_start.day)
                week_checkins = self.checkin_repo.count_checkins(
                    member_id, start_date=week_start, result=CheckinResult.APPROVED.value
                )
                if week_checkins >= 15:
                    denied = self.checkin_repo.create_checkin(
                        member_id, CheckinResult.DENIED.value, 
                        "Entry limits exceeded (daily/weekly)", now
                    )
                    return denied
                
                # All business rules passed - approve check-in
                # Update subscription remaining entries (database operation)
                sub.remaining_entries -= 1
                session.commit()
                
                # Create approved check-in record (database operation)
                approved = self.checkin_repo.create_checkin(
                    member_id, CheckinResult.APPROVED.value, None, now
                )
                return approved
                
            except Exception as e:
                session.rollback()
                logger.error(f"Unexpected error in process_checkin: {str(e)}", exc_info=True)
                # Return a denied checkin for unexpected errors
                try:
                    denied = self.checkin_repo.create_checkin(
                        member_id, CheckinResult.DENIED.value, f"System error: {str(e)}", now
                    )
                    return denied
                except:
                    # If we can't even create a checkin record, re-raise
                    raise
