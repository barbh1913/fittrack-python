"""
Repository for workout plan progress tracking.
Implements performance logging, history tracking, and progress analysis.
"""
from datetime import datetime, timedelta
import uuid
import logging

from backend.app.models.Member import Member
from backend.app.models.Trainer import Trainer
from backend.app.models.WorkoutPlan import WorkoutPlan
from backend.app.models.WorkoutItem import WorkoutItem
from backend.app.models.ProgressLog import ProgressLog
from backend.app.exceptions.exceptions import NotFoundError, AppError

logger = logging.getLogger(__name__)


def _id15():
    return uuid.uuid4().hex[:15]


class db_progress_tracking:
    def __init__(self, db_manager):
        self.SessionLocal = db_manager.SessionLocal

    def log_progress(self, workout_plan_id: str, workout_item_id: str, member_id: str,
                     sets_completed: int, reps_completed: int, weight_used: float = None,
                     duration_minutes: int = None, notes: str = None):
        """
        Log workout progress for a specific exercise.
        Validates that the plan belongs to the member and item belongs to the plan.
        """
        with self.SessionLocal() as session:
            try:
                # Validate workout plan exists and belongs to member
                wp = (
                    session.query(WorkoutPlan)
                    .filter(
                        WorkoutPlan.id == workout_plan_id,
                        WorkoutPlan.member_id == member_id
                    )
                    .first()
                )
                if wp is None:
                    raise NotFoundError("Workout plan not found or does not belong to this member")
                
                # Validate workout item exists and belongs to plan
                item = (
                    session.query(WorkoutItem)
                    .filter(
                        WorkoutItem.id == workout_item_id,
                        WorkoutItem.workout_plan_id == workout_plan_id
                    )
                    .first()
                )
                if item is None:
                    raise NotFoundError("Workout item not found or does not belong to this plan")
                
                # Validate values
                if sets_completed < 0:
                    raise AppError("Sets completed cannot be negative")
                if reps_completed < 0:
                    raise AppError("Reps completed cannot be negative")
                if weight_used is not None and weight_used < 0:
                    raise AppError("Weight used cannot be negative")
                if duration_minutes is not None and duration_minutes < 0:
                    raise AppError("Duration cannot be negative")
                
                # Check for future dates (not allowed)
                # This is handled by using datetime.now() below
                
                # Create progress log
                log = ProgressLog(
                    id=_id15(),
                    workout_plan_id=workout_plan_id,
                    workout_item_id=workout_item_id,
                    member_id=member_id,
                    exercise_name=item.exercise_name,
                    sets_completed=sets_completed,
                    reps_completed=reps_completed,
                    weight_used=weight_used,
                    target_weight=item.target_weight,
                    duration_minutes=duration_minutes,
                    notes=notes,
                    logged_at=datetime.now()
                )
                
                session.add(log)
                session.commit()
                return log
                
            except Exception:
                session.rollback()
                raise

    def get_progress_history(self, workout_plan_id: str, member_id: str, limit: int = 50):
        """
        Get progress history for a workout plan.
        Returns logs ordered by most recent first.
        """
        with self.SessionLocal() as session:
            # Validate plan belongs to member
            wp = (
                session.query(WorkoutPlan)
                .filter(
                    WorkoutPlan.id == workout_plan_id,
                    WorkoutPlan.member_id == member_id
                )
                .first()
            )
            if wp is None:
                raise NotFoundError("Workout plan not found or does not belong to this member")
            
            logs = (
                session.query(ProgressLog, WorkoutItem)
                .join(WorkoutItem, WorkoutItem.id == ProgressLog.workout_item_id)
                .filter(ProgressLog.workout_plan_id == workout_plan_id)
                .order_by(ProgressLog.logged_at.desc())
                .limit(limit)
                .all()
            )
            
            return [
                {
                    "id": log.id,
                    "exercise_name": log.exercise_name,
                    "sets_completed": log.sets_completed,
                    "reps_completed": log.reps_completed,
                    "weight_used": log.weight_used,
                    "target_weight": log.target_weight,
                    "duration_minutes": log.duration_minutes,
                    "notes": log.notes,
                    "logged_at": log.logged_at.isoformat() if log.logged_at else None,
                    "improvement": self._calculate_improvement(log, item)
                }
                for log, item in logs
            ]

    def _calculate_improvement(self, log: ProgressLog, item: WorkoutItem) -> dict:
        """Calculate improvement metrics for a log entry."""
        improvement = {
            "weight_increase": None,
            "reps_increase": None,
            "sets_increase": None
        }
        
        # Compare with target
        if log.target_weight and log.weight_used:
            improvement["weight_increase"] = log.weight_used - log.target_weight
        
        if item.reps and log.reps_completed:
            improvement["reps_increase"] = log.reps_completed - item.reps
        
        if item.sets and log.sets_completed:
            improvement["sets_increase"] = log.sets_completed - item.sets
        
        return improvement

    def get_trainee_progress_summary(self, trainer_id: str):
        """
        Get progress summary for all trainees of a trainer.
        Shows which trainees are progressing well.
        """
        with self.SessionLocal() as session:
            # Get all active workout plans for this trainer
            plans = (
                session.query(WorkoutPlan, Member)
                .join(Member, Member.id == WorkoutPlan.member_id)
                .filter(
                    WorkoutPlan.trainer_id == trainer_id,
                    WorkoutPlan.is_active == True
                )
                .all()
            )
            
            summaries = []
            for wp, member in plans:
                # Get recent logs (last 30 days)
                thirty_days_ago = datetime.now() - timedelta(days=30)
                recent_logs = (
                    session.query(ProgressLog)
                    .filter(
                        ProgressLog.workout_plan_id == wp.id,
                        ProgressLog.logged_at >= thirty_days_ago
                    )
                    .count()
                )
                
                # Get total logs
                total_logs = (
                    session.query(ProgressLog)
                    .filter(ProgressLog.workout_plan_id == wp.id)
                    .count()
                )
                
                # Get latest log date
                latest_log = (
                    session.query(ProgressLog)
                    .filter(ProgressLog.workout_plan_id == wp.id)
                    .order_by(ProgressLog.logged_at.desc())
                    .first()
                )
                
                summaries.append({
                    "member_id": member.id,
                    "member_name": member.fullname,
                    "workout_plan_id": wp.id,
                    "workout_plan_title": wp.title,
                    "total_logs": total_logs,
                    "recent_logs_30d": recent_logs,
                    "last_logged": latest_log.logged_at.isoformat() if latest_log else None,
                    "is_progressing": recent_logs >= 5  # At least 5 logs in last 30 days
                })
            
            return summaries

    def get_member_progress_summary(self, member_id: str):
        """Get progress summary for a member across all their workout plans."""
        with self.SessionLocal() as session:
            plans = (
                session.query(WorkoutPlan)
                .filter(
                    WorkoutPlan.member_id == member_id,
                    WorkoutPlan.is_active == True
                )
                .all()
            )
            
            summaries = []
            for wp in plans:
                # Get progress stats
                logs = (
                    session.query(ProgressLog)
                    .filter(ProgressLog.workout_plan_id == wp.id)
                    .order_by(ProgressLog.logged_at.desc())
                    .limit(10)
                    .all()
                )
                
                summaries.append({
                    "workout_plan_id": wp.id,
                    "workout_plan_title": wp.title,
                    "total_logs": len(logs),
                    "recent_logs": [
                        {
                            "exercise": log.exercise_name,
                            "date": log.logged_at.isoformat() if log.logged_at else None,
                            "weight": log.weight_used,
                            "reps": log.reps_completed
                        }
                        for log in logs[:5]
                    ]
                })
            
            return summaries
