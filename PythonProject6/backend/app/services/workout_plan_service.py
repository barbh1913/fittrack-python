"""
Business Logic Layer for Workout Plan operations.
This service contains all business rules for workout plan management.
It orchestrates database operations through the repository layer.
"""
from backend.app.repositories.workout_plan import db_workout_plans
from backend.app.exceptions.exceptions import NotFoundError, AppError
import logging

logger = logging.getLogger(__name__)


class WorkoutPlanService:
    """
    Service class for workout plan business logic.
    Handles all business rules for workout plans.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the service with database manager.
        
        Args:
            db_manager: SQLManger instance for database access
        """
        self.workout_plan_repo = db_workout_plans(db_manager)
    
    def create_workout_plan(self, trainer_id: str, member_id: str, title: str, items: list, is_active: bool = True):
        """
        Create a workout plan with business validation.
        
        Business Rules:
        - Trainer must exist
        - Member must exist
        - Items must be valid
        
        Args:
            trainer_id: Trainer ID
            member_id: Member ID
            title: Plan title
            items: List of workout items
            is_active: Whether plan is active
            
        Returns:
            WorkoutPlan: Created workout plan object
            
        Raises:
            NotFoundError: If trainer or member not found
            AppError: If creation fails
        """
        # Delegate to repository (contains business validation)
        plan = self.workout_plan_repo.create_workout_plan(trainer_id, member_id, title, items, is_active)
        if not plan:
            raise AppError("Failed to create workout plan")
        return plan
    
    def get_workout_plan_for_member(self, member_id: str, workout_plan_id: str):
        """
        Get full workout plan with all items for a member.
        
        Args:
            member_id: Member ID
            workout_plan_id: Workout plan ID
            
        Returns:
            dict: Plan and items data
            
        Raises:
            NotFoundError: If plan not found or doesn't belong to member
        """
        return self.workout_plan_repo.get_workout_plan_for_member(member_id, workout_plan_id)
    
    def get_all_workout_plans_for_member(self, member_id: str):
        """
        Get all workout plans for a member.
        
        Args:
            member_id: Member ID
            
        Returns:
            list: List of workout plans
        """
        return self.workout_plan_repo.get_all_workout_plans_for_member(member_id)
