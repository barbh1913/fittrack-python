from sqlalchemy import Column, String, Float, Integer, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base
from .enums import PlanType


class Plan(Base):
    __tablename__ = "plans"
    __table_args__ = (
        CheckConstraint(
            f"plan_type IN ('{PlanType.MONTHLY.value}', '{PlanType.YEARLY.value}', '{PlanType.WEEKLY.value}', '{PlanType.DAILY.value}', '{PlanType.VIP.value}')",
            name='check_plan_type'
        ),
    )

    id = Column(String(15), primary_key=True)
    name = Column(String(100), nullable=False)
    plan_type = Column(String(100), nullable=False)  # Renamed from 'type' to avoid Python keyword conflict, stores enum value as string
    price = Column(Float, nullable=False)
    valid_days = Column(Integer, nullable=False)
    max_entries = Column(Integer, nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan")
