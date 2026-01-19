from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base



class WorkoutItem(Base):
    __tablename__ = "workout_items"
    id = Column(String(15), primary_key=True)
    workout_plan_id = Column(String(15), ForeignKey("workout_plans.id"), nullable=False)

    exercise_name = Column(String(100), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    target_weight = Column(Float, nullable=True)
    notes = Column(String(200), nullable=True)

    workout_plan = relationship("WorkoutPlan", back_populates="items")
    progress_logs = relationship("ProgressLog", back_populates="workout_item")
