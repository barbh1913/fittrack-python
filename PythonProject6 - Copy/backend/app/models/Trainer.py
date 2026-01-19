from sqlalchemy.orm import relationship
from .Person import Person


class Trainer(Person):
    """
    Trainer model - inherits from Person.
    
    Demonstrates Inheritance: Trainer inherits common fields (id, fullname, email, phone)
    from Person abstract base class, and adds Trainer-specific relationships.
    """
    __tablename__ = "trainers"
    
    # Inherited from Person:
    # - id (String(15), primary_key)
    # - fullname (String(100))
    # - email (String(100), unique=True)
    # - phone (String(12))
    
    # Trainer-specific relationships
    sessions = relationship("ClassSession", back_populates="trainer")
    workout_plans = relationship("WorkoutPlan", back_populates="trainer")
