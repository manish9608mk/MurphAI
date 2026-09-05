from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    AssignmentNotFoundException,
    PermissionDeniedException,
)
from backend.app.models.assignment import Assignment
from backend.app.models.confirmation import Confirmation
from backend.app.models.payment import Payment
from backend.app.models.reputation import Reputation
from backend.app.models.work import Work
from backend.app.models.worker import Worker
from backend.app.models.job import Job


def create_reputation(
    db: Session,
    work_id: int,
    rating: int,
    comment: str | None,
    current_user_id: int,
):
    """
    Create a reputation record for completed work.

    Only the customer who owns the job can rate the worker.

    Reputation requires:
        Work completed
        ↓
        Customer confirmation
        ↓
        Payment paid
    """

    # ========================================================
    # 1. Find Work
    # ========================================================

    work = (
        db.query(Work)
        .filter(Work.id == work_id)
        .first()
    )

    if not work:
        raise PermissionDeniedException("Work not found")

    # Reputation is only allowed after work is completed.
    if work.status != "completed":
        raise PermissionDeniedException(
            "Reputation can only be created for completed work"
        )

    # ========================================================
    # 2. Find Assignment
    # ========================================================

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == work.assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # ========================================================
    # 3. Find Job
    # ========================================================

    job = (
        db.query(Job)
        .filter(Job.id == assignment.job_id)
        .first()
    )

    if not job:
        raise PermissionDeniedException("Job not found")

    # ========================================================
    # 4. Only Customer Can Give Reputation
    # ========================================================

    if job.customer_id != current_user_id:
        raise PermissionDeniedException(
            "Only the customer can rate this work"
        )

    # ========================================================
    # 5. Work Must Be Confirmed
    # ========================================================

    confirmation = (
        db.query(Confirmation)
        .filter(Confirmation.work_id == work_id)
        .first()
    )

    if not confirmation:
        raise PermissionDeniedException(
            "Work must be confirmed before reputation can be created"
        )

    # ========================================================
    # 6. Payment Must Be Paid
    # ========================================================

    payment = (
        db.query(Payment)
        .filter(Payment.work_id == work_id)
        .first()
    )

    if not payment:
        raise PermissionDeniedException(
            "Payment must exist before reputation can be created"
        )

    if payment.status != "paid":
        raise PermissionDeniedException(
            "Payment must be completed before reputation can be created"
        )

    # ========================================================
    # 7. Prevent Duplicate Reputation
    # ========================================================

    existing_reputation = (
        db.query(Reputation)
        .filter(Reputation.work_id == work_id)
        .first()
    )

    if existing_reputation:
        raise PermissionDeniedException(
            "Reputation already exists for this work"
        )

    # ========================================================
    # 8. Find Worker
    # ========================================================

    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .first()
    )

    if not worker:
        raise PermissionDeniedException(
            "Assigned worker not found"
        )

    # ========================================================
    # 9. Create Reputation
    # ========================================================

    reputation = Reputation(
        work_id=work_id,
        customer_id=current_user_id,
        worker_id=worker.id,
        rating=rating,
        comment=comment,
    )

    db.add(reputation)
    db.commit()
    db.refresh(reputation)

    return reputation


def get_reputation(
    db: Session,
    reputation_id: int,
    current_user_id: int,
):
    """
    Get a reputation record.

    Only the customer who gave the reputation
    or the worker who received it can view it.
    """

    # ========================================================
    # 1. Find Reputation
    # ========================================================

    reputation = (
        db.query(Reputation)
        .filter(Reputation.id == reputation_id)
        .first()
    )

    if not reputation:
        raise PermissionDeniedException(
            "Reputation not found"
        )

    # ========================================================
    # 2. Check Customer Access
    # ========================================================

    is_customer = (
        reputation.customer_id == current_user_id
    )

    # ========================================================
    # 3. Check Worker Access
    # ========================================================

    worker = (
        db.query(Worker)
        .filter(Worker.id == reputation.worker_id)
        .first()
    )

    is_worker = (
        worker is not None
        and worker.user_id == current_user_id
    )

    # ========================================================
    # 4. Authorization
    # ========================================================

    if not is_customer and not is_worker:
        raise PermissionDeniedException(
            "You are not allowed to view this reputation"
        )

    return reputation