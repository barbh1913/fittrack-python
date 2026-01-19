"""
Abstract base class for Person entities (Member and Trainer).
Demonstrates Inheritance: Member and Trainer inherit common fields and behavior from Person.

Note: Uses SQLAlchemy's __abstract__ instead of Python's ABC to avoid metaclass conflicts.
"""
from sqlalchemy import Column, String
from .base import Base


class Person(Base):
    """
    Abstract base class for Person entities.
    
    This class defines common fields shared by Member and Trainer:
    - id: Unique identifier
    - fullname: Full name
    - email: Email address
    - phone: Phone number
    
    Note: This is an abstract class in Python (ABC), but SQLAlchemy uses
    concrete table inheritance, so each subclass has its own table.
    """
    __abstract__ = True  # SQLAlchemy: don't create a table for this class
    
    id = Column(String(15), primary_key=True)
    fullname = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(12), nullable=False)
    
    def __repr__(self):
        """String representation of Person."""
        return f"<{self.__class__.__name__}(id={self.id}, name={self.fullname})>"
