from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConfirmationCreate(BaseModel):
    # The work that the customer wants to confirm.
    work_id: int = Field(gt=0)

    # Optional feedback/comment from the customer.
    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ConfirmationResponse(BaseModel):
    id: int
    work_id: int
    customer_id: int
    comment: str | None
    confirmed_at: datetime
    created_at: datetime

    # Allows Pydantic to read data directly from SQLAlchemy models.
    model_config = ConfigDict(from_attributes=True)