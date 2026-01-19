from backend.app.models.Member import Member
import logging

logger = logging.getLogger(__name__)


"""
Data Access Layer for Member operations.
Repository contains ONLY database CRUD operations - no business logic.
"""
class db_member:
    """Repository for member database operations."""
    
    def __init__(self, db_manager):
        """Initialize with database session manager."""
        self.SessionLocal = db_manager.SessionLocal

    def add_member(self, id, fullname, email, phone):
        """Insert new member record into database."""
        with self.SessionLocal() as session:
            try:
                member = Member(id=id, fullname=fullname, email=email, phone=phone)
                session.add(member)
                session.commit()
                # Detach object from session to prevent "not bound to Session" errors
                session.expunge(member)
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to add member: {e}", exc_info=True)
                return False

    def get_member_by_id(self, id):
        """Retrieve member by ID from database."""
        try:
            with self.SessionLocal() as session:
                member = session.query(Member).filter(Member.id == id).first()
                if member:
                    # Detach object from session to prevent "not bound to Session" errors
                    session.expunge(member)
                return member
        except Exception as e:
            logger.error(f"Database error in get_member_by_id: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def get_all_members(self):
        """Retrieve all members from database, ordered by ID."""
        try:
            with self.SessionLocal() as session:
                members = session.query(Member).order_by(Member.id).all()
                # Detach all objects from session
                for member in members:
                    session.expunge(member)
                return members
        except Exception as e:
            logger.error(f"Database error in get_all_members: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def update_member(self, id, fullname, email, phone):
        """Update existing member record in database."""
        with self.SessionLocal() as session:
            try:
                member = session.query(Member).filter(Member.id == id).first()
                if member is None:
                    logger.warning(f"Member does not exist: {id}")
                    return False
                # Update fields
                member.fullname = fullname
                member.email = email
                member.phone = phone
                session.commit()
                # Detach object from session to prevent "not bound to Session" errors
                session.expunge(member)
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to update member: {e}", exc_info=True)
                # Return False for database errors, let service layer handle business logic errors
                return False
