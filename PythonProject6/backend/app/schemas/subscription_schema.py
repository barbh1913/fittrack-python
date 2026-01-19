from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class SubscriptionBase(BaseModel):
    member_id: str = Field(..., max_length=15, examples=["123456789012345"])
    plan_id: str = Field(..., max_length=15, examples=["PLAN0001"])
    start_date: Optional[datetime] = Field(None, examples=["2026-01-13T10:00:00"])

    model_config = ConfigDict(from_attributes=True)


class SubscriptionAssign(SubscriptionBase):
    pass


class SubscriptionAssignResponse(BaseModel):
    subscription_id: str = Field(..., examples=["a1b2c3d4e5f6g7h"])
    model_config = ConfigDict(from_attributes=True)


class SubscriptionFreezeRequest(BaseModel):
    days: int = Field(..., gt=0, examples=[14])
    model_config = ConfigDict(from_attributes=True)


class SubscriptionStatusResponse(BaseModel):
    status: str = Field(..., examples=["ACTIVE"])
    model_config = ConfigDict(from_attributes=True)
