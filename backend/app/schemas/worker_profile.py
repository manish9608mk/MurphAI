from datetime import datetime

from pydantic import BaseModel


class PublicWorkerReview(BaseModel):
    """
    Customer feedback from a verified completed work record.

    Payment information is intentionally excluded from the
    public worker profile.
    """

    work_id: int
    job_title: str
    completed_at: datetime | None
    rating: int
    comment: str | None


class WorkerPublicProfileResponse(BaseModel):
    """
    Public-facing worker profile.

    This response contains information useful for a customer
    evaluating a worker before making an assignment.
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

    reviews: list[PublicWorkerReview]
