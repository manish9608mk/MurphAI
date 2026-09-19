from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssignmentCreate(BaseModel):
    """
    Data required to create an assignment.
    """

    job_id: int
    worker_id: int


class AssignmentResponse(BaseModel):
    """
    Data returned to the API client.
    """

    id: int
    job_id: int
    worker_id: int
    status: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class WorkerAssignmentResponse(BaseModel):
    """
    Assignment data presented to the assigned worker,
    including the job information needed to act on it.
    """

    id: int
    job_id: int
    worker_id: int
    status: str
    job_title: str
    job_description: str
    location: str
    budget: float
    job_status: str
    created_at: datetime
    updated_at: datetime
