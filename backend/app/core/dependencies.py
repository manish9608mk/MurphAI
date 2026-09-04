from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.exceptions import WorkerNotFoundException
from backend.app.core.security import get_current_user_id
from backend.app.database.database import SessionLocal
from backend.app.models.job import Job
from backend.app.models.worker import Worker


def get_db():
    """
    Provide a database session for each request.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def verify_user_access(action: str):
    """
    Verify that the authenticated user owns
    the requested user resource.
    """

    def dependency(
        user_id: int,
        current_user_id: int = Depends(get_current_user_id),
    ):
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not allowed to {action} this user",
            )

        return current_user_id

    return dependency


def verify_job_access(action: str):
    """
    Verify that the authenticated user owns
    the requested job.
    """

    def dependency(
        job_id: int,
        db: Session = Depends(get_db),
        current_user_id: int = Depends(get_current_user_id),
    ):
        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        if job.customer_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not allowed to {action} this job",
            )

        return current_user_id

    return dependency


def verify_worker_access(action: str):
    """
    Verify that the authenticated user owns
    the requested worker profile.
    """

    def dependency(
        worker_id: int,
        db: Session = Depends(get_db),
        current_user_id: int = Depends(get_current_user_id),
    ):
        worker = (
            db.query(Worker)
            .filter(Worker.id == worker_id)
            .first()
        )

        if not worker:
            raise WorkerNotFoundException()

        if worker.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"You are not allowed to "
                    f"{action} this worker profile"
                ),
            )

        return current_user_id

    return dependency