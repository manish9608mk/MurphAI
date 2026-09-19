from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkCreate(BaseModel):
    """
    Data required to create a Work record.
    """

    assignment_id: int = Field(
        gt=0,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )


class WorkUpdate(BaseModel):
    """
    Data that can be updated while work is being performed.
    """

    description: str | None = Field(
        default=None,
        max_length=2000,
    )


class WorkStatusUpdate(BaseModel):
    """
    Request body used when changing the Work status.
    """

    status: str = Field(
        min_length=1,
        max_length=30,
    )


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

    model_config = ConfigDict(
        from_attributes=True,
    )


class WorkerWorkResponse(BaseModel):
    """
    Work data presented to the assigned worker, including
    the job information needed to continue the workflow.
    """

    id: int
    assignment_id: int
    status: str
    description: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    job_title: str
    job_description: str
    location: str
    budget: float
    job_status: str

    model_config = ConfigDict(
        from_attributes=True,
    )
