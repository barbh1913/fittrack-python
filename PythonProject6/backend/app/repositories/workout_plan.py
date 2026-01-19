from datetime import datetime
import uuid

from backend.app.models.Member import Member
from backend.app.models.Trainer import Trainer
from backend.app.models.WorkoutPlan import WorkoutPlan
from backend.app.models.WorkoutItem import WorkoutItem
from backend.app.exceptions.exceptions import NotFoundError, DuplicateError


class db_workout_plans:
    def __init__(self, db_manager):
        self.SessionLocal = db_manager.SessionLocal

    def create_workout_plan(self, trainer_id: str, member_id: str, title: str, items: list, is_active: bool = True):
        with self.SessionLocal() as session:
            try:
                trainer = session.query(Trainer).filter(Trainer.id == trainer_id).first()
                if trainer is None:
                    raise NotFoundError("Trainer not found")

                member = session.query(Member).filter(Member.id == member_id).first()
                if member is None:
                    raise NotFoundError("Member not found")

                wp_id = uuid.uuid4().hex[:15]

                wp = WorkoutPlan(
                    id=wp_id,
                    member_id=member_id,
                    trainer_id=trainer_id,
                    title=title,
                    created_at=datetime.now(),
                    is_active=is_active
                )

                session.add(wp)

                for it in items:
                    item = WorkoutItem(
                        id=uuid.uuid4().hex[:15],
                        workout_plan_id=wp_id,
                        exercise_name=it["exercise_name"],
                        sets=it["sets"],
                        reps=it["reps"],
                        target_weight=it.get("target_weight"),
                        notes=it.get("notes")
                    )
                    session.add(item)

                session.commit()
                return wp

            except Exception:
                session.rollback()
                raise

    def get_workout_plan_for_member(self, member_id: str, workout_plan_id: str):
        with self.SessionLocal() as session:
            wp = (
                session.query(WorkoutPlan)
                .filter(
                    WorkoutPlan.id == workout_plan_id,
                    WorkoutPlan.member_id == member_id
                )
                .first()
            )
            if wp is None:
                raise NotFoundError("Workout plan not found")

            items = (
                session.query(WorkoutItem)
                .filter(WorkoutItem.workout_plan_id == workout_plan_id)
                .all()
            )

            return {"plan": wp, "items": items}

    def get_all_workout_plans_for_member(self, member_id: str):
        """Get all workout plans for a member with trainer info and items."""
        with self.SessionLocal() as session:
            plans = (
                session.query(WorkoutPlan, Trainer)
                .join(Trainer, Trainer.id == WorkoutPlan.trainer_id)
                .filter(
                    WorkoutPlan.member_id == member_id,
                    WorkoutPlan.is_active == True
                )
                .order_by(WorkoutPlan.created_at.desc())
                .all()
            )
            
            result = []
            for wp, trainer in plans:
                items = (
                    session.query(WorkoutItem)
                    .filter(WorkoutItem.workout_plan_id == wp.id)
                    .limit(6)  # Get first 6 exercises to show in card
                    .all()
                )
                
                result.append({
                    "plan": {
                        "id": wp.id,
                        "title": wp.title,
                        "trainer_id": wp.trainer_id,
                        "trainer_name": getattr(trainer, "fullname", None),
                        "created_at": wp.created_at.isoformat() if wp.created_at else None,
                        "is_active": wp.is_active
                    },
                    "items": [
                        {
                            "id": item.id,
                            "exercise_name": item.exercise_name,
                            "sets": item.sets,
                            "reps": item.reps,
                            "target_weight": item.target_weight,
                            "notes": item.notes
                        }
                        for item in items
                    ],
                    "total_items": session.query(WorkoutItem)
                        .filter(WorkoutItem.workout_plan_id == wp.id)
                        .count()
                })
            
            return result
