"""
Business Logic Layer for Progress Tracking operations.
This service contains all business rules for workout progress logging.
It orchestrates database operations through the repository layer.
"""
from backend.app.repositories.progress_tracking import db_progress_tracking
from backend.app.exceptions.exceptions import NotFoundError, AppError
import logging

logger = logging.getLogger(__name__)


class ProgressService:
    """
    Service class for progress tracking business logic.
    Handles all business rules for workout progress.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the service with database manager.
        
        Args:
            db_manager: SQLManger instance for database access
        """
        self.progress_repo = db_progress_tracking(db_manager)
    
    def log_progress(self, workout_plan_id: str, workout_item_id: str, member_id: str,
                     sets_completed: int, reps_completed: int, weight_used: float = None,
                     duration_minutes: int = None, notes: str = None):
        """
        Log workout progress with business validation.
        
        Business Rules:
        - Workout plan must exist and belong to member
        - Workout item must exist and belong to plan
        - Values cannot be negative
        - Cannot log future dates
        
        Args:
            workout_plan_id: Workout plan ID
            workout_item_id: Workout item ID
            member_id: Member ID
            sets_completed: Number of sets completed
            reps_completed: Number of reps completed
            weight_used: Weight used (optional)
            duration_minutes: Duration in minutes (optional)
            notes: Notes (optional)
            
        Returns:
            ProgressLog: Created progress log object
            
        Raises:
            NotFoundError: If plan/item not found or doesn't belong to member
            AppError: If values are invalid
        """
        # Delegate to repository (contains business validation)
        return self.progress_repo.log_progress(
            workout_plan_id, workout_item_id, member_id,
            sets_completed, reps_completed, weight_used,
            duration_minutes, notes
        )
    
    def get_progress_history(self, workout_plan_id: str, member_id: str, limit: int = 50):
        """
        Get progress history for a workout plan.
        
        Args:
            workout_plan_id: Workout plan ID
            member_id: Member ID
            limit: Maximum number of records to return
            
        Returns:
            list: List of progress log entries
        """
        return self.progress_repo.get_progress_history(workout_plan_id, member_id, limit)
    
    def get_trainer_progress_summary(self, trainer_id: str):
        """
        Get progress summary for all trainees of a trainer.
        
        Args:
            trainer_id: Trainer ID
            
        Returns:
            list: List of trainee progress summaries
        """
        return self.progress_repo.get_trainer_progress_summary(trainer_id)
    
    def get_member_progress_summary(self, member_id: str):
        """
        Get progress summary for a member across all their workout plans.
        
        Args:
            member_id: Member ID
            
        Returns:
            list: List of progress summaries
        """
        return self.progress_repo.get_member_progress_summary(member_id)
