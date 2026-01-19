from sqlalchemy import Column, String, ForeignKey, Float, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base
from .enums import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint(
            f"status IN ('{PaymentStatus.PENDING.value}', '{PaymentStatus.PAID.value}', '{PaymentStatus.FAILED.value}', '{PaymentStatus.REFUNDED.value}')",
            name='check_payment_status'
        ),
    )

    id = Column(String(15), primary_key=True)
    subscription_id = Column(String(15), ForeignKey("subscriptions.id"), nullable=False, index=True) 
    amount = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default=PaymentStatus.PENDING.value)  # Stores enum value as string  
    paid_at = Column(DateTime, nullable=True)  
    reference = Column(String(100), nullable=True)  

    subscription = relationship("Subscription", back_populates="payments")
