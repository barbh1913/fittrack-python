"""
Repository for waiting list/queue management.
Implements queue registration, automatic promotion, and high-demand detection.
"""
from datetime import datetime, timedelta
import uuid
import logging

from backend.app.models.ClassSession import ClassSession
from backend.app.models.Member import Member
from backend.app.models.Subscription import Subscription
from backend.app.models.Plan import Plan
from backend.app.models.Enrollment import Enrollment
from backend.app.models.WaitingList import WaitingList
from backend.app.models.enums import (
    WaitingListStatus, EnrollmentStatus, SessionStatus, 
    SubscriptionStatus, PlanType
)
from backend.app.exceptions.exceptions import NotFoundError, DuplicateError, AppError

logger = logging.getLogger(__name__)


def _id15():
    return uuid.uuid4().hex[:15]


class db_waiting_list:
    def __init__(self, db_manager):
        self.SessionLocal = db_manager.SessionLocal

    def calculate_priority_score(self, member_id: str, created_at: datetime) -> int:
        """
        Calculate priority score for queue positioning.
        Factors: Subscription type (VIP = higher), waiting time.
        """
        with self.SessionLocal() as session:
            # Get active subscription
            sub = (
                session.query(Subscription, Plan)
                .join(Plan, Plan.id == Subscription.plan_id)
                .filter(
                    Subscription.member_id == member_id,
                    Subscription.status == SubscriptionStatus.ACTIVE.value
                )
                .first()
            )
            
            base_score = 0
            if sub:
                plan = sub[1]
                # VIP plans get higher priority
                if plan.plan_type == PlanType.VIP.value:
                    base_score = 1000
                else:
                    base_score = 100
            
            # Waiting time bonus (older entries get slightly higher priority)
            # But VIP still trumps waiting time
            waiting_time_bonus = int((datetime.now() - created_at).total_seconds() / 3600)  # Hours
            
            return base_score + waiting_time_bonus

    def add_to_waiting_list(self, class_session_id: str, member_id: str) -> WaitingList:
        """
        Add a member to the waiting list for a full session.
        Returns the waiting list entry with position and status.
        """
        with self.SessionLocal() as session:
            try:
                # Validate session exists
                cs = session.query(ClassSession).filter(ClassSession.id == class_session_id).first()
                if cs is None:
                    raise NotFoundError("Class session not found")
                
                # Check if session is closed
                if cs.status == SessionStatus.CLOSED.value:
                    raise AppError("Session registration is closed")
                
                # Validate member exists
                member = session.query(Member).filter(Member.id == member_id).first()
                if member is None:
                    raise NotFoundError("Member not found")
                
                # Check if already enrolled
                existing_enrollment = (
                    session.query(Enrollment)
                    .filter(
                        Enrollment.class_session_id == class_session_id,
                        Enrollment.member_id == member_id,
                        Enrollment.status == EnrollmentStatus.REGISTERED.value
                    )
                    .first()
                )
                if existing_enrollment:
                    raise DuplicateError("Member is already enrolled in this session")
                
                # Check if already on waiting list
                existing_wait = (
                    session.query(WaitingList)
                    .filter(
                        WaitingList.class_session_id == class_session_id,
                        WaitingList.member_id == member_id,
                        WaitingList.status.in_([
                            WaitingListStatus.WAITING.value,
                            WaitingListStatus.ASSIGNED.value
                        ])
                    )
                    .first()
                )
                if existing_wait:
                    raise DuplicateError("Member is already on the waiting list")
                
                # Calculate position (count existing waiting entries + 1)
                position = (
                    session.query(WaitingList)
                    .filter(
                        WaitingList.class_session_id == class_session_id,
                        WaitingList.status == WaitingListStatus.WAITING.value
                    )
                    .count()
                ) + 1
                
                # Create waiting list entry
                now = datetime.now()
                priority_score = self.calculate_priority_score(member_id, now)
                
                # Recalculate positions based on priority (higher priority = lower position number)
                # This ensures VIP members are first
                waiting_entries = (
                    session.query(WaitingList)
                    .filter(
                        WaitingList.class_session_id == class_session_id,
                        WaitingList.status == WaitingListStatus.WAITING.value
                    )
                    .all()
                )
                
                # Insert in correct position based on priority
                final_position = position
                for entry in waiting_entries:
                    if priority_score > entry.priority_score:
                        # This entry should be before entry
                        final_position = min(final_position, entry.position)
                    elif priority_score == entry.priority_score:
                        # Same priority, first come first served
                        if now < entry.created_at:
                            final_position = min(final_position, entry.position)
                
                # Adjust positions of entries that come after
                for entry in waiting_entries:
                    if entry.position >= final_position:
                        entry.position += 1
                
                wl_entry = WaitingList(
                    id=_id15(),
                    class_session_id=class_session_id,
                    member_id=member_id,
                    status=WaitingListStatus.WAITING.value,
                    position=final_position,
                    priority_score=priority_score,
                    created_at=now,
                    approval_deadline=None,
                    assigned_at=None,
                    confirmed_at=None,
                    cancelled_at=None
                )
                
                session.add(wl_entry)
                session.commit()
                
                return wl_entry
                
            except Exception:
                session.rollback()
                raise

    def promote_from_queue(self, class_session_id: str, approval_deadline_hours: int = 24) -> WaitingList:
        """
        Automatically promote the first member in queue when a spot becomes available.
        Returns the promoted waiting list entry, or None if queue is empty.
        """
        with self.SessionLocal() as session:
            try:
                # Get first waiting member (lowest position, highest priority)
                first_entry = (
                    session.query(WaitingList)
                    .filter(
                        WaitingList.class_session_id == class_session_id,
                        WaitingList.status == WaitingListStatus.WAITING.value
                    )
                    .order_by(WaitingList.position.asc())
                    .first()
                )
                
                if not first_entry:
                    return None
                
                # Update status to ASSIGNED
                now = datetime.now()
                deadline = now + timedelta(hours=approval_deadline_hours)
                
                first_entry.status = WaitingListStatus.ASSIGNED.value
                first_entry.assigned_at = now
                first_entry.approval_deadline = deadline
                
                # Update positions of remaining entries
                remaining = (
                    session.query(WaitingList)
                    .filter(
                        WaitingList.class_session_id == class_session_id,
                        WaitingList.status == WaitingListStatus.WAITING.value,
                        WaitingList.id != first_entry.id
                    )
                    .all()
                )
                
                for entry in remaining:
                    entry.position = max(1, entry.position - 1)
                
                session.commit()
                return first_entry
                
            except Exception:
                session.rollback()
                raise

    def confirm_assignment(self, waiting_list_id: str) -> Enrollment:
        """
        Confirm assignment and create enrollment.
        Called when member approves the spot.
        """
        with self.SessionLocal() as session:
            try:
                wl_entry = session.query(WaitingList).filter(WaitingList.id == waiting_list_id).first()
                if wl_entry is None:
                    raise NotFoundError("Waiting list entry not found")
                
                if wl_entry.status != WaitingListStatus.ASSIGNED.value:
                    raise AppError("Waiting list entry is not in ASSIGNED status")
                
                # Check if deadline passed
                if wl_entry.approval_deadline and datetime.now() > wl_entry.approval_deadline:
                    # Expire this entry and promote next
                    wl_entry.status = WaitingListStatus.EXPIRED.value
                    session.commit()
                    # Promote next in queue
                    self.promote_from_queue(wl_entry.class_session_id)
                    raise AppError("Approval deadline has passed. Spot has been given to next in queue.")
                
                # Create enrollment
                enrollment = Enrollment(
                    id=_id15(),
                    class_session_id=wl_entry.class_session_id,
                    member_id=wl_entry.member_id,
                    status=EnrollmentStatus.REGISTERED.value,
                    created_at=datetime.now(),
                    canceled_at=None,
                    cancel_reason=None
                )
                
                session.add(enrollment)
                
                # Update waiting list entry
                wl_entry.status = WaitingListStatus.CONFIRMED.value
                wl_entry.confirmed_at = datetime.now()
                
                session.commit()
                # Expunge the object from the session to detach it
                # This prevents "not bound to a Session" errors when accessing it later
                session.expunge(enrollment)
                return enrollment
                
            except Exception:
                session.rollback()
                raise

    def check_expired_assignments(self, class_session_id: str = None):
        """
        Check for expired assignments and automatically promote next in queue.
        Should be called periodically (e.g., via cron job or scheduled task).
        """
        with self.SessionLocal() as session:
            try:
                query = (
                    session.query(WaitingList)
                    .filter(
                        WaitingList.status == WaitingListStatus.ASSIGNED.value,
                        WaitingList.approval_deadline < datetime.now()
                    )
                )
                
                if class_session_id:
                    query = query.filter(WaitingList.class_session_id == class_session_id)
                
                expired = query.all()
                
                for entry in expired:
                    entry.status = WaitingListStatus.EXPIRED.value
                    # Promote next in queue
                    self.promote_from_queue(entry.class_session_id)
                
                session.commit()
                return len(expired)
                
            except Exception:
                session.rollback()
                raise

    def get_waiting_list(self, class_session_id: str):
        """Get full waiting list for a session, ordered by position."""
        with self.SessionLocal() as session:
            entries = (
                session.query(WaitingList, Member)
                .join(Member, Member.id == WaitingList.member_id)
                .filter(WaitingList.class_session_id == class_session_id)
                .order_by(WaitingList.position.asc())
                .all()
            )
            
            return [
                {
                    "id": wl.id,
                    "member_id": wl.member_id,
                    "member_name": m.fullname,
                    "position": wl.position,
                    "status": wl.status,
                    "priority_score": wl.priority_score,
                    "created_at": wl.created_at.isoformat() if wl.created_at else None,
                    "assigned_at": wl.assigned_at.isoformat() if wl.assigned_at else None,
                    "approval_deadline": wl.approval_deadline.isoformat() if wl.approval_deadline else None,
                    "waiting_hours": (datetime.now() - wl.created_at).total_seconds() / 3600 if wl.created_at else 0
                }
                for wl, m in entries
            ]

    def detect_high_demand(self, min_waiting: int = 5, min_waiting_hours: int = 24):
        """
        Detect sessions with high demand.
        Returns sessions with recommendations.
        """
        with self.SessionLocal() as session:
            # Get sessions with waiting lists
            sessions_with_waiting = (
                session.query(ClassSession, WaitingList)
                .join(WaitingList, WaitingList.class_session_id == ClassSession.id)
                .filter(WaitingList.status == WaitingListStatus.WAITING.value)
                .all()
            )
            
            # Group by session
            session_stats = {}
            for cs, wl in sessions_with_waiting:
                if cs.id not in session_stats:
                    session_stats[cs.id] = {
                        "session": cs,
                        "waiting_count": 0,
                        "max_waiting_hours": 0
                    }
                
                session_stats[cs.id]["waiting_count"] += 1
                waiting_hours = (datetime.now() - wl.created_at).total_seconds() / 3600
                session_stats[cs.id]["max_waiting_hours"] = max(
                    session_stats[cs.id]["max_waiting_hours"],
                    waiting_hours
                )
            
            # Filter high-demand sessions
            high_demand = []
            for session_id, stats in session_stats.items():
                if (stats["waiting_count"] >= min_waiting or 
                    stats["max_waiting_hours"] >= min_waiting_hours):
                    high_demand.append({
                        "session_id": session_id,
                        "session_title": stats["session"].title,
                        "waiting_count": stats["waiting_count"],
                        "max_waiting_hours": stats["max_waiting_hours"],
                        "current_capacity": stats["session"].capacity,
                        "recommendations": [
                            "Consider opening an additional session",
                            "Consider increasing capacity if possible"
                        ]
                    })
            
            return high_demand
