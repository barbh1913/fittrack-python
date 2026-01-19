from sqlalchemy import Column, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base
from .enums import CheckinResult


class Checkin(Base):
    __tablename__ = "checkin"
    __table_args__ = (
        CheckConstraint(
            f"result IN ('{CheckinResult.APPROVED.value}', '{CheckinResult.DENIED.value}', '{CheckinResult.PENDING.value}')",
            name='check_checkin_result'
        ),
    )
    
    id = Column(String(15), primary_key=True)
    member_id = Column(String(9), ForeignKey("members.id"), nullable=False)  # Person ID is 9 chars
    created_at = Column(DateTime, nullable=False)
    result = Column(String(50), nullable=False)  # Stores enum value as string
    reason = Column(String(200), nullable=True)

    member = relationship("Member", back_populates="checkins")
