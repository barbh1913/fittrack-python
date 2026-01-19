from pydantic import BaseModel, Field, field_validator, ConfigDict
from backend.app.models.enums import CheckinResult


class CheckinRequest(BaseModel):
    member_id: str = Field(..., max_length=15, examples=["123456789012345"])
    model_config = ConfigDict(from_attributes=True)


class CheckinResponse(BaseModel):
    result: str = Field(..., description="Check-in result status", examples=["APPROVED"])
    reason: str = Field("", description="Reason for approval or denial", examples=[""])
    model_config = ConfigDict(from_attributes=True)

    @field_validator('result')
    @classmethod
    def validate_result(cls, v: str) -> str:
        """Validate that result is a valid CheckinResult enum value."""
        valid_values = [e.value for e in CheckinResult]
        if v not in valid_values:
            raise ValueError(f'Invalid check-in result. Must be one of: {", ".join(valid_values)}')
        return v
