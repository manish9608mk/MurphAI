from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from backend.app.database.database import Base


class Reputation(Base):
    __tablename__ = "reputations"

    # Unique reputation record.
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # The completed work being reviewed.
    # One work can have only one reputation record.
    work_id = Column(
        Integer,
        ForeignKey("works.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    # The customer who gives the reputation.
    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # The worker receiving the reputation.
    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False,
        index=True,
    )

    # Customer rating from 1 to 5.
    rating = Column(
        Integer,
        nullable=False,
    )

    # Optional customer review.
    comment = Column(
        String(2000),
        nullable=True,
    )

    # Time when the reputation was created.
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )