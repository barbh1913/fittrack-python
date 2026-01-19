from .Person import Person


class Admin(Person):
    """
    Admin model - inherits from Person.
    
    Demonstrates Inheritance: Admin inherits common fields (id, fullname, email, phone)
    from Person abstract base class. Admins have elevated privileges to manage
    the entire gym system.
    """
    __tablename__ = "admins"
    
    # Inherited from Person:
    # - id (String(15), primary_key)
    # - fullname (String(100))
    # - email (String(100), unique=True)
    # - phone (String(12))
    
    # Admins don't have specific relationships - they can manage all entities
