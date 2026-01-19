"""
Business Logic Layer for Waiting List operations.
This service contains all business rules for queue management.
It orchestrates database operations through the repository layer.
"""
from backend.app.repositories.waiting_list import db_waiting_list
from backend.app.exceptions.exceptions import NotFoundError, DuplicateError, AppError
import logging

logger = logging.getLogger(__name__)


class WaitingListService:
    """
    Service class for waiting list business logic.
    Handles all business rules for queue management.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the service with database manager.
        
        Args:
            db_manager: SQLManger instance for database access
        """
        self.waiting_list_repo = db_waiting_list(db_manager)
    
    def add_to_waiting_list(self, class_session_id: str, member_id: str):
        """
        Add a member to the waiting list with business validation.
        
        Business Rules:
        - Session must exist
        - Member must exist
        - Member cannot be already enrolled
        - Member cannot be already on waiting list
        
        Args:
            class_session_id: Class session ID
            member_id: Member ID
            
        Returns:
            WaitingList: Created waiting list entry
            
        Raises:
            NotFoundError: If session or member not found
            DuplicateError: If member already enrolled or on waiting list
            AppError: If session registration is closed
        """
        # Delegate to repository (contains business validation)
        return self.waiting_list_repo.add_to_waiting_list(class_session_id, member_id)
    
    def confirm_assignment(self, waiting_list_id: str):
        """
        Confirm assignment and create enrollment.
        
        Business Rules:
        - Waiting list entry must exist and be ASSIGNED
        - Approval deadline must not have passed
        
        Args:
            waiting_list_id: Waiting list entry ID
            
        Returns:
            Enrollment: Created enrollment object
            
        Raises:
            NotFoundError: If waiting list entry not found
            AppError: If assignment expired or invalid
        """
        # Delegate to repository (contains business validation)
        return self.waiting_list_repo.confirm_assignment(waiting_list_id)
    
    def get_waiting_list(self, session_id: str):
        """
        Get full waiting list for a session.
        
        Args:
            session_id: Class session ID
            
        Returns:
            list: List of waiting list entries
        """
        return self.waiting_list_repo.get_waiting_list(session_id)
    
    def get_member_waiting_lists(self, member_id: str):
        """
        Get all waiting list entries for a member.
        
        Args:
            member_id: Member ID
            
        Returns:
            list: List of waiting list entries
        """
        return self.waiting_list_repo.get_member_waiting_list_status(member_id)
    
    def check_expired_assignments(self, session_id: str = None):
        """
        Check for expired assignments and promote next in queue.
        
        Business Rules:
        - ASSIGNED entries past approval deadline are expired
        - Expired entries are moved to EXPIRED status
        - Next member in queue is promoted
        
        Args:
            session_id: Optional session ID to check specific session
            
        Returns:
            int: Count of expired assignments processed
        """
        # Delegate to repository (contains business logic)
        return self.waiting_list_repo.expire_assignments(session_id)
