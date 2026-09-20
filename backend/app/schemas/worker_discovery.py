from pydantic import BaseModel


class WorkerDiscoveryItem(BaseModel):
    """
    Public worker information used by the worker directory.
    """

    worker_id: int
    name: str
    bio: str | None
    location: str | None
    experience_years: int
    is_available: bool
    skills: list[str]
    verified_work_count: int
    average_rating: float | None


class WorkerDiscoveryResponse(BaseModel):
    """
    Paginated public worker discovery response.
    """

    total: int
    workers: list[WorkerDiscoveryItem]
