from backend.app.models.Trainer import Trainer
import logging

logger = logging.getLogger(__name__)


class db_trainer:
    def __init__(self, db_manager):
        self.SessionLocal = db_manager.SessionLocal

    def add_trainer(self, id, fullname, email, phone):
        """Add a new trainer to the database."""
        session = self.SessionLocal()
        try:
            trainer = Trainer(
                id=id,
                fullname=fullname,
                email=email,
                phone=phone
            )
            session.add(trainer)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add trainer: {e}", exc_info=True)
            return False
        finally:
            session.close()

    def get_trainer_by_id(self, id):
        """Get trainer by ID."""
        try:
            with self.SessionLocal() as session:
                return session.query(Trainer).filter(Trainer.id == id).first()
        except Exception as e:
            logger.error(f"Database error in get_trainer_by_id: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def get_all_trainers(self):
        """Get all trainers from the database."""
        try:
            with self.SessionLocal() as session:
                return session.query(Trainer).order_by(Trainer.id).all()
        except Exception as e:
            logger.error(f"Database error in get_all_trainers: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def update_trainer(self, id, fullname, email, phone):
        """Update trainer information."""
        with self.SessionLocal() as session:
            try:
                trainer = session.query(Trainer).filter(Trainer.id == id).first()
                if trainer is None:
                    logger.warning(f"Trainer does not exist: {id}")
                    return False
                trainer.fullname = fullname
                trainer.email = email
                trainer.phone = phone
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to update trainer: {e}", exc_info=True)
                return False
