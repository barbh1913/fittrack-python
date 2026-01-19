"""
Data Access Layer for Check-in operations.
This repository contains ONLY database CRUD operations.
No business logic or validation - that belongs in the Service layer.
"""
from datetime import datetime
import uuid

from backend.app.models.Checkin import Checkin
from backend.app.models.enums import CheckinResult


def _id15():
    """Generate a 15-character ID."""
    return uuid.uuid4().hex[:15]


class db_checkin:
    """
    Repository for check-in database operations.
    Only performs CRUD operations - no business logic.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the repository with database manager.
        
        Args:
            db_manager: SQLManger instance for database access
        """
        self.SessionLocal = db_manager.SessionLocal
    
    def create_checkin(self, member_id: str, result: str, reason: str = None, created_at: datetime = None) -> Checkin:
        """
        Create a check-in record in the database.
        
        Args:
            member_id: Member ID
            result: Check-in result (APPROVED or DENIED)
            reason: Optional denial reason
            created_at: Optional creation timestamp (defaults to now)
            
        Returns:
            Checkin: Created check-in object
        """
        if created_at is None:
            created_at = datetime.now()
        
        with self.SessionLocal() as session:
            try:
                c = Checkin(
                    id=_id15(),
                    member_id=member_id,
                    created_at=created_at,
                    result=result,
                    reason=reason
                )
                session.add(c)
                session.commit()
                # Expunge the object from the session to detach it
                # This prevents "not bound to a Session" errors when accessing it later
                session.expunge(c)
                return c
            except Exception as e:
                session.rollback()
                raise
    
    def get_checkin_by_id(self, checkin_id: str) -> Checkin:
        """
        Get a check-in record by ID.
        
        Args:
            checkin_id: Check-in ID
            
        Returns:
            Checkin: Check-in object or None if not found
        """
        with self.SessionLocal() as session:
            return session.query(Checkin).filter(Checkin.id == checkin_id).first()
    
    def get_member_checkins(self, member_id: str, start_date: datetime = None, 
                           end_date: datetime = None, result: str = None):
        """
        Get check-ins for a member with optional filters.
        
        Args:
            member_id: Member ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            result: Optional result filter (APPROVED or DENIED)
            
        Returns:
            list: List of check-in objects
        """
        with self.SessionLocal() as session:
            query = session.query(Checkin).filter(Checkin.member_id == member_id)
            
            if start_date:
                query = query.filter(Checkin.created_at >= start_date)
            if end_date:
                query = query.filter(Checkin.created_at <= end_date)
            if result:
                query = query.filter(Checkin.result == result)
            
            return query.order_by(Checkin.created_at.desc()).all()
    
    def count_checkins(self, member_id: str, start_date: datetime = None, 
                      end_date: datetime = None, result: str = None) -> int:
        """
        Count check-ins for a member with optional filters.
        
        Args:
            member_id: Member ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            result: Optional result filter (APPROVED or DENIED)
            
        Returns:
            int: Count of check-ins
        """
        with self.SessionLocal() as session:
            query = session.query(Checkin).filter(Checkin.member_id == member_id)
            
            if start_date:
                query = query.filter(Checkin.created_at >= start_date)
            if end_date:
                query = query.filter(Checkin.created_at <= end_date)
            if result:
                query = query.filter(Checkin.result == result)
            
            return query.count()
