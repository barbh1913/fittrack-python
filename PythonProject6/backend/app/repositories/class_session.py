from datetime import datetime
import uuid

from backend.app.models.Trainer import Trainer
from backend.app.models.Member import Member
from backend.app.models.ClassSession import ClassSession
from backend.app.models.Enrollment import Enrollment
from backend.app.models.enums import EnrollmentStatus, SessionStatus
from backend.app.exceptions.exceptions import NotFoundError, DuplicateError, AppError

class db_sessions:
    def __init__(self, db_manager):
        self.SessionLocal = db_manager.SessionLocal
        self.db_manager = db_manager

    def create_session(self, title: str, starts_at: datetime, capacity: int, trainer_id: str, status: SessionStatus = SessionStatus.OPEN):
        with self.SessionLocal() as session:
            try:
                trainer = session.query(Trainer).filter(Trainer.id == trainer_id).first()
                if trainer is None:
                    return False

                ses = ClassSession(
                    id=uuid.uuid4().hex[:15],
                    title=title,
                    starts_at=starts_at,
                    capacity=capacity,
                    trainer_id=trainer_id,
                    status=status.value if isinstance(status, SessionStatus) else status  # Store enum value as string
                )

                session.add(ses)
                session.commit()
                return ses   # ✅ היה return s
            except Exception:
                session.rollback()
                return False

    def enroll_member(self, class_session_id: str, member_id: str):
        """
        Enroll member in class session.
        If session is full, adds member to waiting list instead.
        """
        with self.SessionLocal() as session:
            try:
                # Validate session exists
                cs = session.query(ClassSession).filter(ClassSession.id == class_session_id).first()
                if cs is None:
                    raise NotFoundError("Class session not found")

                # Validate member exists
                member = session.query(Member).filter(Member.id == member_id).first()
                if member is None:
                    raise NotFoundError("Member not found")

                # Check if already enrolled
                existing = (
                    session.query(Enrollment)
                    .filter(
                        Enrollment.class_session_id == class_session_id,
                        Enrollment.member_id == member_id,
                        Enrollment.status == EnrollmentStatus.REGISTERED.value
                    )
                    .first()
                )
                if existing is not None:
                    raise DuplicateError("Member is already enrolled in this session")

                # Check capacity
                current_count = (
                    session.query(Enrollment)
                    .filter(
                        Enrollment.class_session_id == class_session_id,
                        Enrollment.status == EnrollmentStatus.REGISTERED.value
                    )
                    .count()
                )
                if current_count >= cs.capacity:
                    # Session is full - add to waiting list
                    from backend.app.repositories.waiting_list import db_waiting_list
                    waiting_list_repo = db_waiting_list(self.db_manager)
                    wl_entry = waiting_list_repo.add_to_waiting_list(class_session_id, member_id)
                    raise AppError(f"Session is full. You have been added to the waiting list at position {wl_entry.position}.")

                # Create enrollment record
                enrol = Enrollment(
                    id=uuid.uuid4().hex[:15],
                    class_session_id=class_session_id,
                    member_id=member_id,
                    status=EnrollmentStatus.REGISTERED.value,
                    created_at=datetime.now(),
                    canceled_at=None,
                    cancel_reason=None
                )

                session.add(enrol)
                session.commit()
                
                # Verify enrollment was created
                session.refresh(enrol)
                if enrol.status != EnrollmentStatus.REGISTERED.value:
                    raise AppError("Failed to create enrollment")
                
                # Get ID before expunging (access while still in session)
                enrollment_id = enrol.id
                
                # Detach object from session to prevent "not bound to Session" errors
                session.expunge(enrol)
                
                # Create a simple object with just the ID to return
                # This avoids session binding issues when accessing attributes later
                class EnrollmentResult:
                    def __init__(self, enrollment_id):
                        self.id = enrollment_id
                
                result = EnrollmentResult(enrollment_id)
                return result
            except (NotFoundError, DuplicateError, AppError):
                # Re-raise custom exceptions
                session.rollback()
                raise
            except Exception as e:
                session.rollback()
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Unexpected error in enroll_member: {str(e)}", exc_info=True)
                raise AppError(f"Failed to enroll member: {str(e)}")

    def cancel_enrollment(self, class_session_id: str, member_id: str, cancel_reason: str = None):
        """Cancel enrollment and promote next member from waiting list."""
        with self.SessionLocal() as session:
            try:
                # Find the enrollment
                enrol = (
                    session.query(Enrollment)
                    .filter(
                        Enrollment.class_session_id == class_session_id,
                        Enrollment.member_id == member_id,
                        Enrollment.status == EnrollmentStatus.REGISTERED.value
                    )
                    .first()
                )
                if enrol is None:
                    raise NotFoundError("Enrollment not found or already canceled")

                # Update enrollment status
                enrol.status = EnrollmentStatus.CANCELED.value
                enrol.canceled_at = datetime.now()
                enrol.cancel_reason = cancel_reason
                
                # Commit the cancellation first
                session.commit()
                
                # Verify the cancellation was saved
                session.refresh(enrol)
                if enrol.status != EnrollmentStatus.CANCELED.value:
                    raise AppError("Failed to update enrollment status")
                
                # Promote from waiting list when enrollment is canceled (after commit)
                try:
                    from backend.app.repositories.waiting_list import db_waiting_list
                    waiting_list_repo = db_waiting_list(self.db_manager)
                    waiting_list_repo.promote_from_queue(class_session_id)
                except Exception as e:
                    # Log but don't fail the cancellation if waiting list promotion fails
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to promote from waiting list: {str(e)}")
                
                return True
            except (NotFoundError, AppError):
                # Re-raise custom exceptions
                session.rollback()
                raise
            except Exception as e:
                session.rollback()
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Unexpected error in cancel_enrollment: {str(e)}", exc_info=True)
                raise AppError(f"Failed to cancel enrollment: {str(e)}")

    def list_participants(self, class_session_id: str):
        """List all participants for a session, showing only active enrollments."""
        with self.SessionLocal() as session:
            # Get all enrollments for this session, ordered by created_at (newest first)
            rows = (
                session.query(Enrollment, Member)
                .join(Member, Member.id == Enrollment.member_id)
                .filter(Enrollment.class_session_id == class_session_id)
                .order_by(Enrollment.created_at.desc())  # Newest first
                .all()
            )

            # Group by member_id and keep only the most recent enrollment per member
            # This prevents duplicates when a member enrolls, cancels, and re-enrolls
            seen_members = {}
            result = []
            
            for enrol, m in rows:
                member_id = m.id if m else enrol.member_id
                
                # Only add if we haven't seen this member yet (keep first = most recent)
                if member_id not in seen_members:
                    seen_members[member_id] = True
                    result.append({
                        "member_id": member_id,
                        "full_name": m.fullname if m else None,
                        "status": enrol.status
                    })
            
            return result

    def get_weekly_sessions(self, member_id: str = None):
        """Get all sessions for the current week with participant counts."""
        from datetime import datetime, timedelta
        from backend.app.models.Trainer import Trainer
        from backend.app.models.enums import EnrollmentStatus
        
        with self.SessionLocal() as session:
            # Get start and end of current week (Monday to Sunday)
            today = datetime.now().date()
            days_since_monday = today.weekday()
            week_start = datetime.combine(today - timedelta(days=days_since_monday), datetime.min.time())
            week_end = week_start + timedelta(days=7)
            
            # Query sessions for this week
            sessions = (
                session.query(ClassSession, Trainer)
                .join(Trainer, Trainer.id == ClassSession.trainer_id)
                .filter(
                    ClassSession.starts_at >= week_start,
                    ClassSession.starts_at < week_end,
                    ClassSession.status != SessionStatus.CANCELLED.value
                )
                .order_by(ClassSession.starts_at)
                .all()
            )
            
            result = []
            for cs, trainer in sessions:
                # Count registered participants
                participant_count = (
                    session.query(Enrollment)
                    .filter(
                        Enrollment.class_session_id == cs.id,
                        Enrollment.status == EnrollmentStatus.REGISTERED.value
                    )
                    .count()
                )
                
                # Check if member is enrolled
                is_enrolled = False
                if member_id:
                    enrollment = (
                        session.query(Enrollment)
                        .filter(
                            Enrollment.class_session_id == cs.id,
                            Enrollment.member_id == member_id,
                            Enrollment.status == EnrollmentStatus.REGISTERED.value
                        )
                        .first()
                    )
                    is_enrolled = enrollment is not None
                
                result.append({
                    "id": cs.id,
                    "title": cs.title,
                    "starts_at": cs.starts_at.isoformat() if cs.starts_at else None,
                    "capacity": cs.capacity,
                    "current_participants": participant_count,
                    "status": cs.status,
                    "trainer_id": cs.trainer_id,
                    "trainer_name": trainer.fullname if trainer else None,
                    "is_enrolled": is_enrolled
                })
            
            return result

    def get_trainer_sessions(self, trainer_id: str):
        """Get all sessions for a specific trainer with participant counts."""
        from datetime import datetime, timedelta
        from backend.app.models.enums import EnrollmentStatus, SessionStatus
        
        with self.SessionLocal() as session:
            # Get start of current week (Monday)
            today = datetime.now().date()
            days_since_monday = today.weekday()
            week_start = datetime.combine(today - timedelta(days=days_since_monday), datetime.min.time())
            week_end = week_start + timedelta(days=14)  # Get next 2 weeks
            
            # Query sessions for this trainer
            sessions = (
                session.query(ClassSession)
                .filter(
                    ClassSession.trainer_id == trainer_id,
                    ClassSession.starts_at >= week_start,
                    ClassSession.starts_at < week_end,
                    ClassSession.status != SessionStatus.CANCELLED.value
                )
                .order_by(ClassSession.starts_at)
                .all()
            )
            
            result = []
            for cs in sessions:
                # Count registered participants
                participant_count = (
                    session.query(Enrollment)
                    .filter(
                        Enrollment.class_session_id == cs.id,
                        Enrollment.status == EnrollmentStatus.REGISTERED.value
                    )
                    .count()
                )
                
                result.append({
                    "id": cs.id,
                    "title": cs.title,
                    "starts_at": cs.starts_at.isoformat() if cs.starts_at else None,
                    "capacity": cs.capacity,
                    "current_participants": participant_count,
                    "status": cs.status
                })
            
            return result

    def get_all_sessions(self):
        """Get all sessions with trainer info and participant counts."""
        from backend.app.models.enums import EnrollmentStatus
        
        with self.SessionLocal() as session:
            # Query all sessions
            sessions = (
                session.query(ClassSession, Trainer)
                .join(Trainer, Trainer.id == ClassSession.trainer_id)
                .order_by(ClassSession.starts_at.desc())
                .all()
            )
            
            result = []
            for cs, trainer in sessions:
                # Count registered participants
                participant_count = (
                    session.query(Enrollment)
                    .filter(
                        Enrollment.class_session_id == cs.id,
                        Enrollment.status == EnrollmentStatus.REGISTERED.value
                    )
                    .count()
                )
                
                result.append({
                    "id": cs.id,
                    "title": cs.title,
                    "starts_at": cs.starts_at.isoformat() if cs.starts_at else None,
                    "capacity": cs.capacity,
                    "current_participants": participant_count,
                    "status": cs.status,
                    "trainer_id": cs.trainer_id,
                    "trainer_name": trainer.fullname if trainer else None
                })
            
            return result
