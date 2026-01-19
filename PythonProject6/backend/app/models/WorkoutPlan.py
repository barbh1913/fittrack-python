from sqlalchemy import String, Column, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(String(15), primary_key=True)
    member_id = Column(String(9), ForeignKey("members.id"), nullable=False)  # Person ID is 9 chars
    trainer_id = Column(String(9), ForeignKey("trainers.id"), nullable=False)  # Person ID is 9 chars

    title = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False)

    member = relationship("Member", back_populates="workout_plans")
    trainer = relationship("Trainer", back_populates="workout_plans")
    items = relationship("WorkoutItem", back_populates="workout_plan")
    progress_logs = relationship("ProgressLog", back_populates="workout_plan")
