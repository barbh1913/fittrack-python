"""
ProgressLog model for tracking workout plan performance over time.
Demonstrates progress tracking and historical data management.
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Float, Text
from sqlalchemy.orm import relationship
from .base import Base


class ProgressLog(Base):
    __tablename__ = "progress_logs"

    id = Column(String(15), primary_key=True)
    workout_plan_id = Column(String(15), ForeignKey("workout_plans.id"), nullable=False, index=True)
    workout_item_id = Column(String(15), ForeignKey("workout_items.id"), nullable=False, index=True)
    member_id = Column(String(9), ForeignKey("members.id"), nullable=False, index=True)  # Person ID is 9 chars
    
    # Exercise details at time of logging
    exercise_name = Column(String(100), nullable=False)
    sets_completed = Column(Integer, nullable=False)
    reps_completed = Column(Integer, nullable=False)
    weight_used = Column(Float, nullable=True)  # Actual weight used
    target_weight = Column(Float, nullable=True)  # Target weight at time of logging
    
    # Performance metrics
    duration_minutes = Column(Integer, nullable=True)  # Time taken
    notes = Column(Text, nullable=True)  # Member's notes about the session
    
    # Timestamp
    logged_at = Column(DateTime, nullable=False)
    
    # Relationships
    workout_plan = relationship("WorkoutPlan", back_populates="progress_logs")
    workout_item = relationship("WorkoutItem", back_populates="progress_logs")
    member = relationship("Member", back_populates="progress_logs")
