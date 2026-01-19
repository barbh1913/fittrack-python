from sqlalchemy.orm import relationship
from .Person import Person


class Member(Person):
    """
    Member model - inherits from Person.
    
    Demonstrates Inheritance: Member inherits common fields (id, fullname, email, phone)
    from Person abstract base class, and adds Member-specific relationships.
    """
    __tablename__ = "members"
    
    # Inherited from Person:
    # - id (String(15), primary_key)
    # - fullname (String(100))
    # - email (String(100), unique=True)
    # - phone (String(12))
    
    # Member-specific relationships

    subscriptions = relationship("Subscription", back_populates="member")
    enrollments = relationship("Enrollment", back_populates="member")
    checkins = relationship("Checkin", back_populates="member")
    workout_plans = relationship("WorkoutPlan", back_populates="member")
    waiting_list_entries = relationship("WaitingList", back_populates="member")
    progress_logs = relationship("ProgressLog", back_populates="member")
