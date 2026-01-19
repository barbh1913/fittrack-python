from sqlalchemy import Column, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base
from .enums import EnrollmentStatus


class Enrollment(Base):
    __tablename__ = "enrollment"
    __table_args__ = (
        CheckConstraint(
            f"status IN ('{EnrollmentStatus.REGISTERED.value}', '{EnrollmentStatus.CANCELED.value}', '{EnrollmentStatus.ATTENDED.value}', '{EnrollmentStatus.NO_SHOW.value}')",
            name='check_enrollment_status'
        ),
    )

    id = Column(String(15), primary_key=True)
    class_session_id = Column(String(15), ForeignKey("class_session.id"), nullable=False)
    member_id = Column(String(9), ForeignKey("members.id"), nullable=False)  # Person ID is 9 chars
    status = Column(String(20), nullable=False, default=EnrollmentStatus.REGISTERED.value)  # Stores enum value as string

    created_at = Column(DateTime, nullable=False)
    canceled_at = Column(DateTime, nullable=True)
    cancel_reason = Column(String(200), nullable=True)

    session = relationship("ClassSession", back_populates="enrollments")
    member = relationship("Member", back_populates="enrollments")
