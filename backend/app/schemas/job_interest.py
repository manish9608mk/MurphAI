from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobInterestCreate(BaseModel):
    """
    Data required for a worker to express
    interest in a job.
    """

    job_id: int = Field(
        gt=0,
    )


class JobInterestResponse(BaseModel):
    """
    Data returned to the API client.
    """

    id: int
    job_id: int
    worker_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )