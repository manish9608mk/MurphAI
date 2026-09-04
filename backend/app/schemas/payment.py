from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    # The work this payment is for.
    work_id: int = Field(gt=0)

    # Payment amount.
    amount: float = Field(gt=0)

    # Optional reference from a future payment provider
    # such as Stripe or Razorpay.
    transaction_reference: str | None = Field(
        default=None,
        max_length=200,
    )


class PaymentResponse(BaseModel):
    id: int
    work_id: int
    customer_id: int
    worker_id: int
    amount: float
    status: str
    transaction_reference: str | None
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime

    # Allows Pydantic to read data from SQLAlchemy models.
    model_config = ConfigDict(from_attributes=True)