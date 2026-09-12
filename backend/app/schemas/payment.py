from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# MurphAI Payment Schemas

class PaymentCreate(BaseModel):
    # The work this payment is for.
    work_id: int = Field(gt=0)

    # Optional reference from a future payment provider
    # such as Stripe or Razorpay.
    transaction_reference: str | None = Field(
        default=None,
        max_length=200,
    )

    # Reject unexpected fields such as a client-supplied amount.
    model_config = ConfigDict(
        extra="forbid",
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

    model_config = ConfigDict(
        from_attributes=True,
    )