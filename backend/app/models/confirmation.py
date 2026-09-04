from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from backend.app.database.database import Base


class Confirmation(Base):
    __tablename__ = "confirmations"

    id = Column(Integer, primary_key=True, index=True)

    # The work being confirmed.
    # One completed work can have only one confirmation.
    work_id = Column(
        Integer,
        ForeignKey("works.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    # The customer who confirms the work.
    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Optional message from the customer.
    comment = Column(
        String(2000),
        nullable=True,
    )

    # Time when the customer confirmed the work.
    confirmed_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # Record creation time.
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )