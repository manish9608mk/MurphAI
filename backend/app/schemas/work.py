from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Create Work
# ============================================================

class WorkCreate(BaseModel):
    """
    Data required to create a Work record.

    Work is created for an accepted Assignment.
    """

    # ID of the assignment for which the work is being created.
    assignment_id: int = Field(
        gt=0,
    )

    # Optional description of the actual work.
    #
    # Example:
    # "Replaced damaged electrical wiring."
    description: str | None = Field(
        default=None,
        max_length=2000,
    )


# ============================================================
# Update Work
# ============================================================

class WorkUpdate(BaseModel):
    """
    Data that can be updated while work is being performed.

    We intentionally do NOT allow the client to directly
    change assignment_id here.
    """

    # Description of the work performed.
    description: str | None = Field(
        default=None,
        max_length=2000,
    )


# ============================================================
# Change Work Status
# ============================================================

class WorkStatusUpdate(BaseModel):
    """
    Request body used when changing the Work status.

    Example:

        {
            "status": "in_progress"
        }
    """

    # Allowed values will be validated by the service layer.
    #
    # pending
    # in_progress
    # completed
    status: str = Field(
        min_length=1,
        max_length=30,
    )


# ============================================================
# Work Response
# ============================================================

class WorkResponse(BaseModel):
    """
    Data returned to the API client.
    """

    id: int

    assignment_id: int

    status: str

    description: str | None

    started_at: datetime | None

    completed_at: datetime | None

    created_at: datetime

    updated_at: datetime

    # Allows Pydantic to read data directly from
    # our SQLAlchemy Work model.
    model_config = ConfigDict(
        from_attributes=True,
    )