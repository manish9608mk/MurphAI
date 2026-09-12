# MurphAI Database Configuration

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.app.core.config import settings


# Database Configuration

DATABASE_URL = settings.database_url


# SQLAlchemy Engine

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# Database Session

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# SQLAlchemy Base

Base = declarative_base()