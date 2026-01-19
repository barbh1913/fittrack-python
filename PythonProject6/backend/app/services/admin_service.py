"""
Business Logic Layer for Admin operations.
This service contains all business rules and validation for admins.
It orchestrates database operations through the repository layer.
"""
from backend.app.repositories.admin import db_admin
from backend.app.exceptions.exceptions import NotFoundError, DuplicateError, AppError
import logging

logger = logging.getLogger(__name__)


class AdminService:
    """
    Service class for admin business logic.
    Handles all business rules, validation, and orchestrates repository calls.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the service with database manager.
        
        Args:
            db_manager: SQLManger instance for database access
        """
        self.admin_repo = db_admin(db_manager)
    
    def create_admin(self, admin_id: str, fullname: str, email: str, phone: str):
        """
        Create a new admin with business validation.
        
        Business Rules:
        - Admin ID must be unique
        - Email must be unique (enforced by database)
        
        Args:
            admin_id: Admin ID
            fullname: Full name
            email: Email address
            phone: Phone number
            
        Returns:
            Admin: Created admin object
            
        Raises:
            DuplicateError: If admin with this ID already exists
            AppError: If creation fails
        """
        # Business validation: Check if admin already exists
        existing = self.admin_repo.get_admin_by_id(admin_id)
        if existing is not None:
            raise DuplicateError("Admin with this ID already exists")
        
        # Delegate to repository for database operation
        success = self.admin_repo.add_admin(admin_id, fullname, email, phone)
        if not success:
            raise AppError("Failed to create admin")
        
        # Retrieve and return the created admin
        admin = self.admin_repo.get_admin_by_id(admin_id)
        if admin is None:
            raise AppError("Admin created but could not be retrieved")
        
        return admin
    
    def get_admin(self, admin_id: str):
        """
        Get an admin by ID.
        
        Args:
            admin_id: Admin ID
            
        Returns:
            Admin: Admin object
            
        Raises:
            NotFoundError: If admin not found
        """
        admin = self.admin_repo.get_admin_by_id(admin_id)
        if admin is None:
            raise NotFoundError("Admin not found")
        return admin
    
    def get_all_admins(self):
        """
        Get all admins.
        
        Returns:
            list: List of all admins
        """
        return self.admin_repo.get_all_admins()
    
    def update_admin(self, admin_id: str, fullname: str = None, email: str = None, phone: str = None):
        """
        Update admin information with business validation.
        
        Business Rules:
        - Admin must exist
        - Only provided fields are updated
        
        Args:
            admin_id: Admin ID
            fullname: New full name (optional)
            email: New email (optional)
            phone: New phone (optional)
            
        Returns:
            Admin: Updated admin object
            
        Raises:
            NotFoundError: If admin not found
            AppError: If update fails
        """
        # Business validation: Check if admin exists
        admin = self.admin_repo.get_admin_by_id(admin_id)
        if admin is None:
            raise NotFoundError("Admin not found")
        
        # Prepare update data (only non-None fields)
        update_fullname = fullname if fullname is not None else admin.fullname
        update_email = email if email is not None else admin.email
        update_phone = phone if phone is not None else admin.phone
        
        # Delegate to repository for database operation
        success = self.admin_repo.update_admin(admin_id, update_fullname, update_email, update_phone)
        if not success:
            raise AppError("Failed to update admin")
        
        # Retrieve and return the updated admin
        updated_admin = self.admin_repo.get_admin_by_id(admin_id)
        return updated_admin
