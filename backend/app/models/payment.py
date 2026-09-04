from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from backend.app.database.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    # The work this payment is for.
    # One work can have one payment record.
    work_id = Column(
        Integer,
        ForeignKey("works.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    # The customer who makes the payment.
    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # The worker who receives the payment.
    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False,
        index=True,
    )

    # Amount paid for the work.
    amount = Column(
        Float,
        nullable=False,
    )

    # Simple payment lifecycle.
    # pending → paid
    # pending → failed
    status = Column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    # Optional reference from a payment provider.
    # We are not integrating Stripe/Razorpay yet.
    transaction_reference = Column(
        String(200),
        nullable=True,
    )

    # Time when payment was completed.
    paid_at = Column(
        DateTime,
        nullable=True,
    )

    # Record creation time.
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # Record update time.
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )