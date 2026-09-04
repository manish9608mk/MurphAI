from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.sql import func

from backend.app.database.database import Base


# This table connects workers and skills.
#
# One worker can have many skills.
# One skill can belong to many workers.
#
# Example:
#
# Worker 1 → electrician
# Worker 1 → wiring
# Worker 2 → electrician
#
worker_skills = Table(
    "worker_skills",
    Base.metadata,

    Column(
        "worker_id",
        Integer,
        ForeignKey("workers.id", ondelete="CASCADE"),
        primary_key=True,
    ),

    Column(
        "skill_id",
        Integer,
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Human-readable skill name.
    #
    # Example:
    # "Electrician"
    # "Plumbing"
    # "AC Repair"
    name = Column(
        String(100),
        nullable=False,
    )

    # Lowercase normalized version used
    # to prevent duplicates such as:
    #
    # Electrician
    # electrician
    # ELECTRICIAN
    normalized_name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )