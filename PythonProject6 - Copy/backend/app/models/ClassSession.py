from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base
from .enums import SessionStatus


class ClassSession(Base):
    __tablename__ = "class_session"
    __table_args__ = (
        CheckConstraint(
            f"status IN ('{SessionStatus.OPEN.value}', '{SessionStatus.FULL.value}', '{SessionStatus.CANCELLED.value}', '{SessionStatus.COMPLETED.value}', '{SessionStatus.CLOSED.value}')",
            name='check_session_status'
        ),
    )

    id = Column(String(15), primary_key=True)
    title = Column(String(100), nullable=False)
    starts_at = Column(DateTime, nullable=False)  
    capacity = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default=SessionStatus.OPEN.value)  # Stores enum value as string 

    trainer_id = Column(String(9), ForeignKey("trainers.id"), nullable=False, index=True)  # Person ID is 9 chars
    trainer = relationship("Trainer", back_populates="sessions")

    enrollments = relationship("Enrollment", back_populates="session")
    waiting_list = relationship("WaitingList", back_populates="session", order_by="WaitingList.position")
