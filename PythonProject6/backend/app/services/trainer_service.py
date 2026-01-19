"""
Business Logic Layer for Trainer operations.
This service contains all business rules and validation for trainers.
It orchestrates database operations through the repository layer.
"""
from backend.app.repositories.trainer import db_trainer
from backend.app.exceptions.exceptions import NotFoundError, DuplicateError, AppError
import logging

logger = logging.getLogger(__name__)


class TrainerService:
    """
    Service class for trainer business logic.
    Handles all business rules, validation, and orchestrates repository calls.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the service with database manager.
        
        Args:
            db_manager: SQLManger instance for database access
        """
        self.trainer_repo = db_trainer(db_manager)
    
    def create_trainer(self, trainer_id: str, fullname: str, email: str, phone: str):
        """
        Create a new trainer with business validation.
        
        Business Rules:
        - Trainer ID must be unique
        - Email must be unique (enforced by database)
        
        Args:
            trainer_id: Trainer ID
            fullname: Full name
            email: Email address
            phone: Phone number
            
        Returns:
            Trainer: Created trainer object
            
        Raises:
            DuplicateError: If trainer with this ID already exists
            AppError: If creation fails
        """
        # Business validation: Check if trainer already exists
        existing = self.trainer_repo.get_trainer_by_id(trainer_id)
        if existing is not None:
            raise DuplicateError("Trainer with this ID already exists")
        
        # Delegate to repository for database operation
        success = self.trainer_repo.add_trainer(trainer_id, fullname, email, phone)
        if not success:
            raise AppError("Failed to create trainer")
        
        # Retrieve and return the created trainer
        trainer = self.trainer_repo.get_trainer_by_id(trainer_id)
        if trainer is None:
            raise AppError("Trainer created but could not be retrieved")
        
        return trainer
    
    def get_trainer(self, trainer_id: str):
        """
        Get a trainer by ID.
        
        Args:
            trainer_id: Trainer ID
            
        Returns:
            Trainer: Trainer object
            
        Raises:
            NotFoundError: If trainer not found
        """
        trainer = self.trainer_repo.get_trainer_by_id(trainer_id)
        if trainer is None:
            raise NotFoundError("Trainer not found")
        return trainer
    
    def get_all_trainers(self):
        """
        Get all trainers.
        
        Returns:
            list: List of all trainers
        """
        return self.trainer_repo.get_all_trainers()
    
    def update_trainer(self, trainer_id: str, fullname: str = None, email: str = None, phone: str = None):
        """
        Update trainer information with business validation.
        
        Business Rules:
        - Trainer must exist
        - Only provided fields are updated
        
        Args:
            trainer_id: Trainer ID
            fullname: New full name (optional)
            email: New email (optional)
            phone: New phone (optional)
            
        Returns:
            Trainer: Updated trainer object
            
        Raises:
            NotFoundError: If trainer not found
            AppError: If update fails
        """
        # Business validation: Check if trainer exists
        trainer = self.trainer_repo.get_trainer_by_id(trainer_id)
        if trainer is None:
            raise NotFoundError("Trainer not found")
        
        # Prepare update data (only non-None fields)
        update_fullname = fullname if fullname is not None else trainer.fullname
        update_email = email if email is not None else trainer.email
        update_phone = phone if phone is not None else trainer.phone
        
        # Delegate to repository for database operation
        success = self.trainer_repo.update_trainer(trainer_id, update_fullname, update_email, update_phone)
        if not success:
            raise AppError("Failed to update trainer")
        
        # Retrieve and return the updated trainer
        updated_trainer = self.trainer_repo.get_trainer_by_id(trainer_id)
        return updated_trainer
