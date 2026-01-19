from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List


class WorkoutPlanCreateRequest(BaseModel):
    trainer_id: str = Field(..., max_length=15, examples=["TR1234567890123"])
    member_id: str = Field(..., max_length=15, examples=["123456789012345"])
    title: str = Field(..., max_length=100, examples=["Upper Body - Week 1"])
    items: List[Dict[str, Any]] = Field(..., examples=[[{"exercise": "Push Ups", "sets": 3, "reps": 12}]])

    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanCreateResponse(BaseModel):
    workout_plan_id: str = Field(..., examples=["wp123456789012"])
    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanViewResponse(BaseModel):
    plan: str = Field(..., examples=["wp123456789012"])
    items_count: int = Field(..., examples=[5])
    model_config = ConfigDict(from_attributes=True)
