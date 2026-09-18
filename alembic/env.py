from logging.config import fileConfig

from sqlalchemy import pool

from alembic import context

from backend.app.core.config import settings
from backend.app.database.database import Base


# Import your models so SQLAlchemy knows about them
from backend.app.models.user import User
from backend.app.models.job import Job
from backend.app.models.worker import Worker
from backend.app.models.skill import Skill
from backend.app.models.assignment import Assignment
from backend.app.models.work import Work
from backend.app.models.evidence import Evidence
from backend.app.models.confirmation import Confirmation
from backend.app.models.payment import Payment
from backend.app.models.reputation import Reputation
from backend.app.models.job_interest import JobInterest


# Alembic Config object
config = context.config


# Configure Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata
# Alembic uses this to compare the current database
# with your Python models.
target_metadata = Base.metadata


# Use the same database URL as the MurphAI application.
config.set_main_option(
    "sqlalchemy.url",
    settings.database_url,
)


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.

    Offline mode generates SQL without creating
    an actual database connection.
    """

    url = settings.database_url

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in online mode.

    Online mode connects to the actual database
    and applies migrations.
    """

    from sqlalchemy import create_engine

    engine = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()