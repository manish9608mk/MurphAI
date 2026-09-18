from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from backend.app.database.database import Base


class JobInterest(Base):
    """
    Represents a worker's interest in an open job.

    One worker can express interest in a job only once.
    """

    __tablename__ = "job_interests"

    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "worker_id",
            name="uq_job_interests_job_worker",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False,
        index=True,
    )

    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False,
        index=True,
    )

    # Interest lifecycle:
    #
    # pending
    # withdrawn
    # rejected
    # selected
    status = Column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )