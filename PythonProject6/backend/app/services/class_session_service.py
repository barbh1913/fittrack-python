"""
Business Logic Layer for Class Session operations.
This service contains all business rules for class session and enrollment management.
It orchestrates database operations through the repository layer.
"""
from datetime import datetime

from backend.app.repositories.class_session import db_sessions
from backend.app.repositories.waiting_list import db_waiting_list
from backend.app.models.enums import SessionStatus, EnrollmentStatus
from backend.app.exceptions.exceptions import NotFoundError, DuplicateError, AppError
import logging

logger = logging.getLogger(__name__)


class ClassSessionService:
    """
    Service class for class session business logic.
    Handles all business rules for sessions and enrollments.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the service with database manager.
        
        Args:
            db_manager: SQLManger instance for database access
        """
        self.session_repo = db_sessions(db_manager)
        self.db_manager = db_manager
    
    def create_session(self, title: str, starts_at: datetime, capacity: int, trainer_id: str, 
                      status: SessionStatus = SessionStatus.OPEN):
        """
        Create a new class session with business validation.
        
        Business Rules:
        - Trainer must exist (validated by repository)
        - Capacity must be positive
        
        Args:
            title: Session title
            starts_at: Session start datetime
            capacity: Maximum capacity
            trainer_id: Trainer ID
            status: Session status (default: OPEN)
            
        Returns:
            ClassSession: Created session object
            
        Raises:
            NotFoundError: If trainer not found
            AppError: If creation fails
        """
        # Business validation: Capacity must be positive
        if capacity <= 0:
            raise AppError("Session capacity must be greater than 0")
        
        # Delegate to repository
        session = self.session_repo.create_session(title, starts_at, capacity, trainer_id, status)
        if not session:
            raise AppError("Failed to create session")
        
        return session
    
    def enroll_member(self, class_session_id: str, member_id: str):
        """
        Enroll a member in a class session with business validation.
        
        Business Rules:
        - Session must exist
        - Member must exist
        - Member cannot be already enrolled
        - If session is full, add to waiting list
        
        Args:
            class_session_id: Class session ID
            member_id: Member ID
            
        Returns:
            Enrollment or WaitingList: Enrollment if successful, WaitingList if added to queue
            
        Raises:
            NotFoundError: If session or member not found
            DuplicateError: If member already enrolled
            AppError: If session is full (member added to waiting list)
        """
        # Delegate to repository (contains business logic for waiting list)
        return self.session_repo.enroll_member(class_session_id, member_id)
    
    def cancel_enrollment(self, class_session_id: str, member_id: str, cancel_reason: str = None):
        """
        Cancel a member's enrollment with business validation.
        
        Business Rules:
        - Enrollment must exist and be REGISTERED
        - After cancellation, promote next member from waiting list
        
        Args:
            class_session_id: Class session ID
            member_id: Member ID
            cancel_reason: Optional cancellation reason
            
        Returns:
            bool: True if successful
            
        Raises:
            NotFoundError: If enrollment not found
            AppError: If cancellation fails
        """
        # Delegate to repository (contains business logic for waiting list promotion)
        return self.session_repo.cancel_enrollment(class_session_id, member_id, cancel_reason)
    
    def list_participants(self, class_session_id: str):
        """
        List all participants for a session.
        
        Args:
            class_session_id: Class session ID
            
        Returns:
            list: List of participant data
        """
        return self.session_repo.list_participants(class_session_id)
    
    def get_weekly_sessions(self, member_id: str = None):
        """
        Get all sessions for the current week.
        
        Args:
            member_id: Optional member ID to filter by enrollment
            
        Returns:
            list: List of session data
        """
        return self.session_repo.get_weekly_sessions(member_id)
    
    def get_trainer_sessions(self, trainer_id: str):
        """
        Get all sessions for a trainer.
        
        Args:
            trainer_id: Trainer ID
            
        Returns:
            list: List of session data
        """
        return self.session_repo.get_trainer_sessions(trainer_id)
    
    def get_all_sessions(self):
        """
        Get all sessions with participant counts.
        
        Returns:
            list: List of session data
        """
        return self.session_repo.get_all_sessions()
