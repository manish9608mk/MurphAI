from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReputationCreate(BaseModel):
    # The completed work being reviewed.
    work_id: int = Field(gt=0)

    # Customer rating from 1 to 5.
    rating: int = Field(ge=1, le=5)

    # Optional customer review.
    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ReputationResponse(BaseModel):
    id: int
    work_id: int
    customer_id: int
    worker_id: int
    rating: int
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)