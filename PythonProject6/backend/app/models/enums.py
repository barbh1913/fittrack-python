"""
Enum classes for status values to prevent typos and enforce valid states.
This demonstrates Encapsulation by restricting status values to predefined options.
"""
from enum import Enum


class SubscriptionStatus(Enum):
    """Subscription status values."""
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    EXPIRED = "EXPIRED"
    BLOCKED = "BLOCKED"  # Added for debt-based blocking
    # Note: EXPIRED is calculated, not stored directly
    
    def __str__(self):
        return self.value


class SessionStatus(Enum):
    """Class session status values."""
    OPEN = "OPEN"
    FULL = "FULL"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"  # Registration closed early
    
    def __str__(self):
        return self.value


class EnrollmentStatus(Enum):
    """Enrollment status values."""
    REGISTERED = "REGISTERED"
    CANCELED = "CANCELED"
    ATTENDED = "ATTENDED"
    NO_SHOW = "NO_SHOW"
    
    def __str__(self):
        return self.value


class PaymentStatus(Enum):
    """Payment status values."""
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELED = "CANCELED"  # Added for canceled payments
    
    def __str__(self):
        return self.value


class CheckinResult(Enum):
    """Check-in result values."""
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    PENDING = "PENDING"
    
    def __str__(self):
        return self.value


class PlanType(Enum):
    """Subscription plan type values."""
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    WEEKLY = "WEEKLY"
    DAILY = "DAILY"
    VIP = "VIP"  # Added for VIP priority in queue
    
    def __str__(self):
        return self.value


class WaitingListStatus(Enum):
    """Waiting list status values."""
    WAITING = "WAITING"
    ASSIGNED = "ASSIGNED"  # Spot available, waiting for approval
    CONFIRMED = "CONFIRMED"  # Approved and enrolled
    EXPIRED = "EXPIRED"  # Approval deadline passed
    CANCELLED = "CANCELLED"
    
    def __str__(self):
        return self.value
