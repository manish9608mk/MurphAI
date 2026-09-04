from sqlalchemy.orm import Session

from backend.app.models.job import Job
from backend.app.schemas.job import JobCreate, JobUpdate

from backend.app.core.exceptions import (
    JobNotFoundException,
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

    job.title = job_data.title
    job.description = job_data.description
    job.location = job_data.location
    job.budget = job_data.budget
    job.status = job_data.status

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