from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base
from .enums import SubscriptionStatus


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint(
            f"status IN ('{SubscriptionStatus.ACTIVE.value}', '{SubscriptionStatus.FROZEN.value}', '{SubscriptionStatus.EXPIRED.value}', '{SubscriptionStatus.BLOCKED.value}')",
            name='check_subscription_status'
        ),
    )

    id = Column(String(15), primary_key=True)
    member_id = Column(String(9), ForeignKey("members.id"), nullable=False)  # Person ID is 9 chars
    plan_id = Column(String(15), ForeignKey("plans.id"), nullable=False)
    status = Column(String(20), nullable=False, default=SubscriptionStatus.ACTIVE.value)  # Stores enum value as string
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    remaining_entries = Column(Integer, nullable=False)
    frozen_until = Column(DateTime, nullable=True)
    outstanding_debt = Column(Integer, nullable=False, default=0)  # Debt in cents/currency units

    member = relationship("Member", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")
