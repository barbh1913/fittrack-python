"""
Pydantic schemas for Member API endpoints with regex validations.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

# Import regex patterns from utils
from backend.app.utils.regex_patterns import (
    EMAIL_PATTERN,
    PHONE_PATTERN_IL,
    PHONE_PATTERN_INTL,
    ID_PATTERN,
    FULLNAME_PATTERN,
    PASSWORD_PATTERN
)


class MemberCreateRequest(BaseModel):
    """Request schema for creating a new member."""
    id: str = Field(..., max_length=15, description="Member ID (9 digits)", examples=["123456789"])
    fullname: str = Field(..., max_length=100, description="Full name", examples=["John Doe"])
    email: str = Field(..., max_length=100, description="Email address", examples=["john@example.com"])
    phone: str = Field(..., max_length=12, description="Phone number", examples=["0501234567"])

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format using regex."""
        if not EMAIL_PATTERN.match(v):
            raise ValueError('Invalid email format. Must be a valid email address.')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number (Israeli or international format)."""
        if not (PHONE_PATTERN_IL.match(v) or PHONE_PATTERN_INTL.match(v)):
            raise ValueError('Invalid phone format.')
        return v

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate member ID (9 digits)."""
        if not ID_PATTERN.match(v):
            raise ValueError('Invalid ID format. Must be exactly 9 digits.')
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


class MemberUpdateRequest(BaseModel):
    """Request schema for updating a member."""
    fullname: Optional[str] = Field(None, max_length=100, description="Full name", examples=["John Doe"])
    email: Optional[str] = Field(None, max_length=100, description="Email address", examples=["john@example.com"])
    phone: Optional[str] = Field(None, max_length=12, description="Phone number", examples=["0501234567"])

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format using regex."""
        if v is not None and not EMAIL_PATTERN.match(v):
            raise ValueError('Invalid email format. Must be a valid email address.')
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
            if not FULLNAME_PATTERN.match(v):
                raise ValueError('Invalid name format. Must be 2-100 characters, letters and spaces only.')
            if len(v.strip()) < 2:
                raise ValueError('Name must be at least 2 characters long.')
            return v.strip()
        return v

    model_config = ConfigDict(from_attributes=True)


class MemberResponse(BaseModel):
    """Response schema for member data."""
    id: str = Field(..., examples=["123456789"])
    fullname: str = Field(..., examples=["John Doe"])
    email: str = Field(..., examples=["john@example.com"])
    phone: str = Field(..., examples=["0501234567"])

    model_config = ConfigDict(from_attributes=True)
