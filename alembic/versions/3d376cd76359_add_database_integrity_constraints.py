"""add database integrity constraints

Revision ID: 3d376cd76359
Revises: b3161ee1d24c
Create Date: 2026-09-12 20:33:05.885225

"""
from typing import Sequence, Union

from alembic import op


# Revision identifiers, used by Alembic.
revision: str = "3d376cd76359"
down_revision: Union[str, Sequence[str], None] = "b3161ee1d24c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add database integrity constraints."""
    op.create_check_constraint(
        "ck_jobs_budget_positive",
        "jobs",
        "budget > 0",
    )

    op.create_check_constraint(
        "ck_workers_experience_non_negative",
        "workers",
        "experience_years >= 0",
    )


def downgrade() -> None:
    """Remove database integrity constraints."""
    op.drop_constraint(
        "ck_workers_experience_non_negative",
        "workers",
        type_="check",
    )

    op.drop_constraint(
        "ck_jobs_budget_positive",
        "jobs",
        type_="check",
    )