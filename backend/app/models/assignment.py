from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from backend.app.database.database import Base


class Assignment(Base):
    """
    Connects one Job with one Worker.

    Example:

    Job #10
        ↓
    Worker #5

    The assignment starts as "pending".
    """

    __tablename__ = "assignments"

    # Unique assignment ID.
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # The job being assigned.
    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False,
        index=True,
    )

    # The worker receiving the assignment.
    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False,
        index=True,
    )

    # Assignment state:
    #
    # pending
    # accepted
    # rejected
    # cancelled
    status = Column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    # When the assignment was created.
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # When the assignment was last changed.
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )