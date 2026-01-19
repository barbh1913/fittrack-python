"""
WaitingList model for queue management when sessions are full.
Demonstrates queue management and automatic promotion logic.
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base
from .enums import WaitingListStatus


class WaitingList(Base):
    __tablename__ = "waiting_list"
    __table_args__ = (
        CheckConstraint(
            f"status IN ('{WaitingListStatus.WAITING.value}', '{WaitingListStatus.ASSIGNED.value}', '{WaitingListStatus.CONFIRMED.value}', '{WaitingListStatus.EXPIRED.value}', '{WaitingListStatus.CANCELLED.value}')",
            name='check_waiting_list_status'
        ),
    )

    id = Column(String(15), primary_key=True)
    class_session_id = Column(String(15), ForeignKey("class_session.id"), nullable=False, index=True)
    member_id = Column(String(9), ForeignKey("members.id"), nullable=False, index=True)  # Person ID is 9 chars
    status = Column(String(20), nullable=False, default=WaitingListStatus.WAITING.value)
    
    # Queue position (1 = first in line)
    position = Column(Integer, nullable=False)
    
    # Priority factors
    priority_score = Column(Integer, nullable=False, default=0)  # Higher = more priority
    
    # Approval deadline for ASSIGNED status
    approval_deadline = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False)
    assigned_at = Column(DateTime, nullable=True)  # When spot became available
    confirmed_at = Column(DateTime, nullable=True)  # When member confirmed
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("ClassSession", back_populates="waiting_list")
    member = relationship("Member", back_populates="waiting_list_entries")
