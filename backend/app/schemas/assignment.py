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