from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from backend.app.database.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    bio = Column(
        Text,
        nullable=True,
    )

    location = Column(
        String(200),
        nullable=True,
    )

    experience_years = Column(
        Integer,
        nullable=False,
        default=0,
    )

    is_available = Column(
        Boolean,
        nullable=False,
        default=True,
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