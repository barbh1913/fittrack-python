"""
Business Logic Layer for Member operations.
This service contains all business rules and validation for members.
It orchestrates database operations through the repository layer.
"""
from backend.app.repositories.member import db_member
from backend.app.exceptions.exceptions import NotFoundError, DuplicateError, AppError
import logging

logger = logging.getLogger(__name__)


class MemberService:
    """
    Service class for member business logic.
    Handles all business rules, validation, and orchestrates repository calls.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the service with database manager.
        
        Args:
            db_manager: SQLManger instance for database access
        """
        self.member_repo = db_member(db_manager)
    
    def create_member(self, member_id: str, fullname: str, email: str, phone: str):
        """
        Create a new member with business validation.
        
        Business Rules:
        - Member ID must be unique
        - Email must be unique (enforced by database)
        
        Args:
            member_id: Member ID (9 digits)
            fullname: Full name
            email: Email address
            phone: Phone number
            
        Returns:
            Member: Created member object
            
        Raises:
            DuplicateError: If member with this ID already exists
            AppError: If creation fails
        """
        # Business validation: Check if member already exists
        existing = self.member_repo.get_member_by_id(member_id)
        if existing is not None:
            raise DuplicateError("Member with this ID already exists")
        
        # Delegate to repository for database operation
        success = self.member_repo.add_member(member_id, fullname, email, phone)
        if not success:
            raise AppError("Failed to create member")
        
        # Retrieve and return the created member
        member = self.member_repo.get_member_by_id(member_id)
        if member is None:
            raise AppError("Member created but could not be retrieved")
        
        return member
    
    def get_member(self, member_id: str):
        """
        Get a member by ID.
        
        Args:
            member_id: Member ID
            
        Returns:
            Member: Member object
            
        Raises:
            NotFoundError: If member not found
        """
        member = self.member_repo.get_member_by_id(member_id)
        if member is None:
            raise NotFoundError("Member not found")
        return member
    
    def get_all_members(self):
        """
        Get all members.
        
        Returns:
            list: List of all members
        """
        return self.member_repo.get_all_members()
    
    def update_member(self, member_id: str, fullname: str = None, email: str = None, phone: str = None):
        """
        Update member information with business validation.
        
        Business Rules:
        - Member must exist
        - Only provided fields are updated
        
        Args:
            member_id: Member ID
            fullname: New full name (optional)
            email: New email (optional)
            phone: New phone (optional)
            
        Returns:
            Member: Updated member object
            
        Raises:
            NotFoundError: If member not found
            AppError: If update fails
        """
        # Business validation: Check if member exists
        member = self.member_repo.get_member_by_id(member_id)
        if member is None:
            raise NotFoundError("Member not found")
        
        # Prepare update data (only non-None fields)
        update_fullname = fullname if fullname is not None else member.fullname
        update_email = email if email is not None else member.email
        update_phone = phone if phone is not None else member.phone
        
        # Delegate to repository for database operation
        try:
            success = self.member_repo.update_member(member_id, update_fullname, update_email, update_phone)
            if not success:
                raise AppError("Failed to update member")
        except Exception as e:
            # If repository raises an exception, wrap it
            logger.error(f"Error updating member in repository: {str(e)}", exc_info=True)
            raise AppError(f"Failed to update member: {str(e)}")
        
        # Retrieve and return the updated member
        updated_member = self.member_repo.get_member_by_id(member_id)
        if updated_member is None:
            raise AppError("Member updated but could not be retrieved")
        return updated_member
