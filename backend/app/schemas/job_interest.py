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

class JobInterestWorkerResponse(BaseModel):
    """
    Job interest plus the worker profile information
    needed by the customer to review an interested worker.
    """

    id: int
    job_id: int
    worker_id: int
    status: str

    worker_name: str
    bio: str | None
    location: str | None
    experience_years: int
    is_available: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )