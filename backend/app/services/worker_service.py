from sqlalchemy.orm import Session

from backend.app.models.worker import Worker
from backend.app.schemas.worker import (
    WorkerCreate,
    WorkerUpdate,
)

from backend.app.core.exceptions import (
    WorkerNotFoundException,
    WorkerAlreadyExistsException,
)


def create_worker(
    db: Session,
    worker_data: WorkerCreate,
    user_id: int,
):
    existing_worker = (
        db.query(Worker)
        .filter(Worker.user_id == user_id)
        .first()
    )

    if existing_worker:
        raise WorkerAlreadyExistsException()

    worker = Worker(
        user_id=user_id,
        bio=worker_data.bio,
        location=worker_data.location,
        experience_years=worker_data.experience_years,
        is_available=worker_data.is_available,
    )

    db.add(worker)
    db.commit()
    db.refresh(worker)

    return worker


def get_workers(db: Session):
    return db.query(Worker).all()


def get_worker(
    db: Session,
    worker_id: int,
):
    worker = (
        db.query(Worker)
        .filter(Worker.id == worker_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    return worker


def update_worker(
    db: Session,
    worker_id: int,
    worker_data: WorkerUpdate,
):
    worker = (
        db.query(Worker)
        .filter(Worker.id == worker_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    worker.bio = worker_data.bio
    worker.location = worker_data.location
    worker.experience_years = worker_data.experience_years
    worker.is_available = worker_data.is_available

    db.commit()
    db.refresh(worker)

    return worker


def delete_worker(
    db: Session,
    worker_id: int,
):
    worker = (
        db.query(Worker)
        .filter(Worker.id == worker_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    db.delete(worker)
    db.commit()