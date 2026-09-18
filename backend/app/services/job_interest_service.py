from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    InvalidJobInterestTransitionException,
    JobInterestAlreadyExistsException,
    JobInterestNotFoundException,
    JobNotFoundException,
    PermissionDeniedException,
    WorkerNotFoundException,
    WorkerUnavailableException,
)
from backend.app.models.job import Job
from backend.app.models.job_interest import JobInterest
from backend.app.models.worker import Worker


def create_job_interest(
    db: Session,
    job_id: int,
    current_user_id: int,
):
    """
    Worker expresses interest in an open job.

    Rules:

    1. Job must exist.
    2. Job must be open.
    3. Worker profile must exist.
    4. Worker must be available.
    5. Worker cannot apply to their own job.
    6. A pending interest cannot be duplicated.
    7. A withdrawn interest can be submitted again.

    The Job row is locked before checking its state so
    a concurrent job assignment cannot race with interest creation.
    """

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .with_for_update()
        .first()
    )

    if not job:
        raise JobNotFoundException()

    if job.status != "open":
        raise InvalidJobInterestTransitionException(
            "Cannot express interest in a job "
            f"with status: {job.status}"
        )

    worker = (
        db.query(Worker)
        .filter(Worker.user_id == current_user_id)
        .with_for_update()
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    if job.customer_id == current_user_id:
        raise PermissionDeniedException(
            "You cannot express interest in your own job"
        )

    if not worker.is_available:
        raise WorkerUnavailableException()

    existing_interest = (
        db.query(JobInterest)
        .filter(
            JobInterest.job_id == job_id,
            JobInterest.worker_id == worker.id,
        )
        .with_for_update()
        .first()
    )

    if existing_interest:
        if existing_interest.status == "withdrawn":
            existing_interest.status = "pending"

            db.commit()
            db.refresh(existing_interest)

            return existing_interest

        raise JobInterestAlreadyExistsException()

    interest = JobInterest(
        job_id=job_id,
        worker_id=worker.id,
        status="pending",
    )

    db.add(interest)
    db.commit()
    db.refresh(interest)

    return interest


def get_my_job_interests(
    db: Session,
    current_user_id: int,
):
    """
    Return all job interests belonging to the
    authenticated worker.
    """

    worker = (
        db.query(Worker)
        .filter(Worker.user_id == current_user_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    return (
        db.query(JobInterest)
        .filter(
            JobInterest.worker_id == worker.id
        )
        .order_by(JobInterest.created_at.desc())
        .all()
    )


def get_job_interests(
    db: Session,
    job_id: int,
    current_user_id: int,
):
    """
    Return interests submitted for a job.

    Only the customer who owns the job can
    access this list.
    """

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise JobNotFoundException()

    if job.customer_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to view interests "
            "for this job"
        )

    return (
        db.query(JobInterest)
        .filter(
            JobInterest.job_id == job_id
        )
        .order_by(JobInterest.created_at.asc())
        .all()
    )


def withdraw_job_interest(
    db: Session,
    interest_id: int,
    current_user_id: int,
):
    """
    Worker withdraws their own pending interest.

    Transition:

        pending -> withdrawn
    """

    interest = (
        db.query(JobInterest)
        .filter(JobInterest.id == interest_id)
        .with_for_update()
        .first()
    )

    if not interest:
        raise JobInterestNotFoundException()

    worker = (
        db.query(Worker)
        .filter(Worker.id == interest.worker_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to withdraw this job interest"
        )

    if interest.status != "pending":
        raise InvalidJobInterestTransitionException(
            "Only pending job interests can be withdrawn"
        )

    interest.status = "withdrawn"

    db.commit()
    db.refresh(interest)

    return interest