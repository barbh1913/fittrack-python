from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ClassSessionBase(BaseModel):
    title: str = Field(..., max_length=100, examples=["Yoga"])
    starts_at: datetime = Field(..., examples=["2026-01-20T18:00:00"])
    capacity: int = Field(..., gt=0, examples=[20])
    trainer_id: str = Field(..., max_length=15, examples=["TR1234567890123"])
    status: Optional[str] = Field("OPEN", examples=["OPEN"])

    model_config = ConfigDict(from_attributes=True)


class ClassSessionCreate(ClassSessionBase):
    pass


class ClassSessionCreateResponse(BaseModel):
    session_id: str = Field(..., examples=["sess123456789012"])
    model_config = ConfigDict(from_attributes=True)


class EnrollmentCreateRequest(BaseModel):
    member_id: str = Field(..., max_length=15, examples=["123456789012345"])
    model_config = ConfigDict(from_attributes=True)


class EnrollmentCreateResponse(BaseModel):
    enrollment_id: str = Field(..., examples=["enr123456789012"])
    model_config = ConfigDict(from_attributes=True)


class EnrollmentCancelRequest(BaseModel):
    member_id: str = Field(..., max_length=15, examples=["123456789012345"])
    cancel_reason: Optional[str] = Field(None, max_length=200, examples=["Not available"])

    model_config = ConfigDict(from_attributes=True)


class ParticipantResponse(BaseModel):
    member_id: str = Field(..., max_length=15, examples=["123456789012345"])
    full_name: Optional[str] = Field(None, max_length=100, examples=["Bar Atias"])
    status: str = Field(..., examples=["REGISTERED"])

    model_config = ConfigDict(from_attributes=True)
