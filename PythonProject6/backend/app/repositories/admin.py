from backend.app.models.Admin import Admin
import logging

logger = logging.getLogger(__name__)


class db_admin:
    def __init__(self, db_manager):
        self.SessionLocal = db_manager.SessionLocal

    def add_admin(self, id, fullname, email, phone):
        """Add a new admin to the database."""
        session = self.SessionLocal()
        try:
            admin = Admin(
                id=id,
                fullname=fullname,
                email=email,
                phone=phone
            )
            session.add(admin)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add admin: {e}", exc_info=True)
            return False
        finally:
            session.close()

    def get_admin_by_id(self, id):
        """Get admin by ID."""
        try:
            with self.SessionLocal() as session:
                return session.query(Admin).filter(Admin.id == id).first()
        except Exception as e:
            logger.error(f"Database error in get_admin_by_id: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def get_all_admins(self):
        """Get all admins from the database."""
        try:
            with self.SessionLocal() as session:
                return session.query(Admin).order_by(Admin.id).all()
        except Exception as e:
            logger.error(f"Database error in get_all_admins: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def update_admin(self, id, fullname, email, phone):
        """Update admin information."""
        with self.SessionLocal() as session:
            try:
                admin = session.query(Admin).filter(Admin.id == id).first()
                if admin is None:
                    logger.warning(f"Admin does not exist: {id}")
                    return False
                admin.fullname = fullname
                admin.email = email
                admin.phone = phone
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to update admin: {e}", exc_info=True)
                return False
