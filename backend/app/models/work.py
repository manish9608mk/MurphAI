from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from backend.app.database.database import Base


class Work(Base):
    """
    Represents the actual work performed by a worker
    for an accepted assignment.

    Relationship:

        Job
         ↓
      Assignment
         ↓
        Work

    Example:

        Job #10
        "Fix electrical wiring"

             ↓

        Assignment #7
        Worker #5

             ↓

        Work #3
        status = "in_progress"
    """

    __tablename__ = "works"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    # Unique ID for this work record.
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # --------------------------------------------------------
    # Assignment Relationship
    # --------------------------------------------------------

    # Every Work record belongs to exactly one Assignment.
    #
    # We use assignment_id instead of storing job_id
    # and worker_id again because the Assignment already
    # connects the Job and Worker.
    #
    # This keeps our database normalized.
    assignment_id = Column(
        Integer,
        ForeignKey("assignments.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    # --------------------------------------------------------
    # Work Status
    # --------------------------------------------------------

    # Current state of the actual work.
    #
    # Initial state:
    #     pending
    #
    # Then:
    #     pending → in_progress → completed
    #
    # We can later add "cancelled" if the business logic
    # requires it.
    status = Column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    # --------------------------------------------------------
    # Work Description
    # --------------------------------------------------------

    # Optional notes describing what was actually done.
    #
    # Example:
    # "Replaced damaged wiring and tested the circuit."
    description = Column(
        String(2000),
        nullable=True,
    )

    # --------------------------------------------------------
    # Time Tracking
    # --------------------------------------------------------

    # When the worker actually started the work.
    #
    # This remains NULL until work starts.
    started_at = Column(
        DateTime,
        nullable=True,
    )

    # When the worker completed the work.
    #
    # This remains NULL until work is completed.
    completed_at = Column(
        DateTime,
        nullable=True,
    )

    # --------------------------------------------------------
    # Record Timestamps
    # --------------------------------------------------------

    # When this Work record was created.
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # When this Work record was last modified.
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )