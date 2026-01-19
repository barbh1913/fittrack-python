"""
Business Logic Layer for Subscription operations.
This service contains all business rules for subscription management.
It orchestrates database operations through the repository layer.
"""
from datetime import datetime, timedelta

from backend.app.repositories.subscription import db_Subscription
from backend.app.repositories.member import db_member
from backend.app.models.enums import SubscriptionStatus
from backend.app.exceptions.exceptions import NotFoundError, DuplicateError, AppError
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    Service class for subscription business logic.
    Handles all business rules for subscription management.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the service with database manager.
        
        Args:
            db_manager: SQLManger instance for database access
        """
        self.subscription_repo = db_Subscription(db_manager)
        self.member_repo = db_member(db_manager)
    
    def assign_subscription(self, member_id: str, plan_id: str, start_date: datetime = None):
        """
        Assign a subscription to a member with business validation.
        
        Business Rules:
        - Member must exist
        - Plan must exist
        - Member cannot have multiple active subscriptions
        
        Args:
            member_id: Member ID
            plan_id: Plan ID
            start_date: Start date (defaults to now)
            
        Returns:
            Subscription: Created subscription object
            
        Raises:
            NotFoundError: If member or plan not found
            DuplicateError: If member already has an active subscription
            AppError: If assignment fails
        """
        # Business validation: Check if member exists
        member = self.member_repo.get_member_by_id(member_id)
        if member is None:
            raise NotFoundError("Member not found")
        
        # Delegate to repository (repository will check plan and active subscription)
        return self.subscription_repo.assign_subscription(member_id, plan_id, start_date)
    
    def freeze_subscription(self, subscription_id: str, days: int):
        """
        Freeze a subscription with business validation.
        
        Business Rules:
        - Subscription must exist
        - Subscription must be active
        - Freeze period is added to existing freeze if already frozen
        
        Args:
            subscription_id: Subscription ID
            days: Number of days to freeze
            
        Returns:
            Subscription: Updated subscription object
            
        Raises:
            NotFoundError: If subscription not found
            DuplicateError: If subscription is not active
            AppError: If freeze fails
        """
        # Delegate to repository (repository contains business validation)
        return self.subscription_repo.freeze_subscription(subscription_id, days)
    
    def unfreeze_subscription(self, subscription_id: str):
        """
        Unfreeze a subscription with business validation.
        
        Business Rules:
        - Subscription must exist
        - Subscription must be frozen
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            Subscription: Updated subscription object
            
        Raises:
            NotFoundError: If subscription not found
            DuplicateError: If subscription is not frozen
            AppError: If unfreeze fails
        """
        # Delegate to repository (repository contains business validation)
        return self.subscription_repo.unfreeze_subscription(subscription_id)
    
    def get_subscription_status(self, subscription_id: str):
        """
        Get the current status of a subscription.
        
        Business Logic:
        - Calculates expiration status based on dates
        - Returns FROZEN if frozen, EXPIRED if outside date range, ACTIVE otherwise
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            str: Subscription status (ACTIVE, FROZEN, or EXPIRED)
            
        Raises:
            NotFoundError: If subscription not found
        """
        return self.subscription_repo.get_subscription_status(subscription_id)
