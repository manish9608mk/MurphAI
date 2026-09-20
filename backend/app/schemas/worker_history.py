from datetime import datetime

from pydantic import BaseModel

from backend.app.schemas.confirmation import ConfirmationResponse
from backend.app.schemas.evidence import EvidenceResponse
from backend.app.schemas.payment import PaymentResponse
from backend.app.schemas.reputation import ReputationResponse


class VerifiedWorkHistoryItem(BaseModel):
    """
    A single verified piece of work completed by a worker.

    Verification requires:
        Work completed
        ↓
        Customer confirmation
        ↓
        Payment paid

    Reputation is optional because a customer may
    choose not to submit a rating.
    """

    work_id: int
    assignment_id: int

    job_id: int
    job_title: str
    job_description: str
    location: str
    budget: float
    job_status: str

    work_description: str | None
    started_at: datetime | None
    completed_at: datetime | None

    evidence: list[EvidenceResponse]

    confirmation: ConfirmationResponse
    payment: PaymentResponse
    reputation: ReputationResponse | None


class WorkerVerifiedHistoryResponse(BaseModel):
    """
    Verified professional history for the authenticated worker.
    """

    worker_id: int
    total_verified_works: int
    average_rating: float | None

    works: list[VerifiedWorkHistoryItem]
