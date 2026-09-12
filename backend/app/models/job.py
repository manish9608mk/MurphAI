from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from backend.app.database.database import Base


# MurphAI Job Model

class Job(Base):
    __tablename__ = "jobs"

    __table_args__ = (
        CheckConstraint(
            "budget > 0",
            name="ck_jobs_budget_positive",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String(100),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    location = Column(
        String(200),
        nullable=False,
    )

    budget = Column(
        Float,
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        default="open",
    )

    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )