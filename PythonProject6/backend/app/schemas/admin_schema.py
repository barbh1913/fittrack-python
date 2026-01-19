"""
Pydantic schemas for Admin API endpoints with regex validations.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

# Import regex patterns from utils
from backend.app.utils.regex_patterns import (
    EMAIL_PATTERN,
    PHONE_PATTERN_IL,
    PHONE_PATTERN_INTL,
    FULLNAME_PATTERN
)


class AdminCreateRequest(BaseModel):
    """Request schema for creating a new admin."""
    id: str = Field(..., max_length=9, description="Admin ID (up to 9 chars, alphanumeric)", examples=["ADMIN001"])
    fullname: str = Field(..., max_length=100, description="Full name", examples=["John Admin"])
    email: str = Field(..., max_length=100, description="Email address", examples=["admin@gym.com"])
    phone: str = Field(..., max_length=12, description="Phone number", examples=["0501234567"])

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format using regex."""
        if not EMAIL_PATTERN.match(v):
            raise ValueError('Invalid email format.')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number (Israeli or international format)."""
        if not (PHONE_PATTERN_IL.match(v) or PHONE_PATTERN_INTL.match(v)):
            raise ValueError('Invalid phone format.')
        return v

    @field_validator('fullname')
    @classmethod
    def validate_fullname(cls, v: str) -> str:
        """Validate full name (2-100 characters, letters and spaces only)."""
        v = v.strip()
        if not FULLNAME_PATTERN.match(v):
            raise ValueError('Invalid name format. Must be 2-100 characters, letters and spaces only.')
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters long.')
        return v

    model_config = ConfigDict(from_attributes=True)


class AdminUpdateRequest(BaseModel):
    """Request schema for updating an admin."""
    fullname: Optional[str] = Field(None, max_length=100, description="Full name", examples=["John Admin"])
    email: Optional[str] = Field(None, max_length=100, description="Email address", examples=["admin@gym.com"])
    phone: Optional[str] = Field(None, max_length=12, description="Phone number", examples=["0501234567"])

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format using regex."""
        if v is not None and not EMAIL_PATTERN.match(v):
            raise ValueError('Invalid email format.')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number (Israeli or international format)."""
        if v is not None and not (PHONE_PATTERN_IL.match(v) or PHONE_PATTERN_INTL.match(v)):
            raise ValueError('Invalid phone format.')
        return v

    @field_validator('fullname')
    @classmethod
    def validate_fullname(cls, v: Optional[str]) -> Optional[str]:
        """Validate full name (2-100 characters, letters and spaces only)."""
        if v is not None:
            v = v.strip()
            if not FULLNAME_PATTERN.match(v):
                raise ValueError('Invalid name format. Must be 2-100 characters, letters and spaces only.')
            if len(v) < 2:
                raise ValueError('Name must be at least 2 characters long.')
            return v
        return v

    model_config = ConfigDict(from_attributes=True)


class AdminResponse(BaseModel):
    """Response schema for admin data."""
    id: str = Field(..., examples=["ADMIN001"])
    fullname: str = Field(..., examples=["John Admin"])
    email: str = Field(..., examples=["admin@gym.com"])
    phone: str = Field(..., examples=["0501234567"])

    model_config = ConfigDict(from_attributes=True)
