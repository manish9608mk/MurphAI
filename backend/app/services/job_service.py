# Job Services

from sqlalchemy.orm import Session

from backend.app.models.job import Job
from backend.app.schemas.job import (
    JobCreate,
    JobUpdate,
)

from backend.app.core.exceptions import (
    JobNotFoundException,
    InvalidJobStatusTransitionException,
)

from backend.app.core.job_status import (
    is_valid_transition,
)


def create_job(
    db: Session,
    job_data: JobCreate,
    customer_id: int,
):
    job = Job(
        title=job_data.title,
        description=job_data.description,
        location=job_data.location,
        budget=job_data.budget,
        customer_id=customer_id,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def get_jobs(db: Session):
    return db.query(Job).all()


def get_job(
    db: Session,
    job_id: int,
):
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise JobNotFoundException()

    return job


def update_job(
    db: Session,
    job_id: int,
    job_data: JobUpdate,
):
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise JobNotFoundException()

    # Once a job has been assigned,
    # its budget becomes financially authoritative.
    #
    # Do not allow the budget to change after
    # the job leaves the open state.
    if job.status != "open" and job.budget != job_data.budget:
        raise InvalidJobStatusTransitionException(
            "Job budget cannot be changed after assignment"
        )

    job.title = job_data.title
    job.description = job_data.description
    job.location = job_data.location

    # Budget can only change while the job is open.
    if job.status == "open":
        job.budget = job_data.budget

    db.commit()
    db.refresh(job)

    return job


def update_job_status(
    db: Session,
    job_id: int,
    new_status: str,
):
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise JobNotFoundException()

    if not is_valid_transition(
        job.status,
        new_status,
    ):
        raise InvalidJobStatusTransitionException(
            f"Invalid job status transition: "
            f"{job.status} -> {new_status}"
        )

    job.status = new_status

    db.commit()
    db.refresh(job)

    return job


def delete_job(
    db: Session,
    job_id: int,
):
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise JobNotFoundException()

    db.delete(job)
    db.commit()