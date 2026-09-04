from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    AssignmentNotFoundException,
    PermissionDeniedException,
)
from backend.app.models.assignment import Assignment
from backend.app.models.confirmation import Confirmation
from backend.app.models.job import Job
from backend.app.models.work import Work


def create_confirmation(
    db: Session,
    work_id: int,
    comment: str | None,
    current_user_id: int,
):
    """
    Create a confirmation for completed work.

    Only the customer who owns the job can confirm the work.
    """

    # Find the work.
    work = db.query(Work).filter(Work.id == work_id).first()

    if not work:
        raise PermissionDeniedException("Work not found")

    # Confirmation is only allowed after work is completed.
    if work.status != "completed":
        raise PermissionDeniedException(
            "Only completed work can be confirmed"
        )

    # Find the assignment connected to this work.
    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == work.assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # Find the job connected to the assignment.
    job = db.query(Job).filter(Job.id == assignment.job_id).first()

    if not job:
        raise PermissionDeniedException("Job not found")

    # Only the customer who created the job can confirm it.
    if job.customer_id != current_user_id:
        raise PermissionDeniedException(
            "Only the customer can confirm this work"
        )

    # Make sure the work has not already been confirmed.
    existing_confirmation = (
        db.query(Confirmation)
        .filter(Confirmation.work_id == work_id)
        .first()
    )

    if existing_confirmation:
        raise PermissionDeniedException(
            "Work has already been confirmed"
        )

    # Create the confirmation.
    confirmation = Confirmation(
        work_id=work_id,
        customer_id=current_user_id,
        comment=comment,
    )

    db.add(confirmation)
    db.commit()
    db.refresh(confirmation)

    return confirmation


def get_confirmation(
    db: Session,
    confirmation_id: int,
    current_user_id: int,
):
    """
    Get a confirmation.

    Only the customer or assigned worker can view it.
    """

    # Find the confirmation.
    confirmation = (
        db.query(Confirmation)
        .filter(Confirmation.id == confirmation_id)
        .first()
    )

    if not confirmation:
        raise PermissionDeniedException("Confirmation not found")

    # Find the work.
    work = db.query(Work).filter(Work.id == confirmation.work_id).first()

    if not work:
        raise PermissionDeniedException("Work not found")

    # Find the assignment.
    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == work.assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # Find the job.
    job = db.query(Job).filter(Job.id == assignment.job_id).first()

    if not job:
        raise PermissionDeniedException("Job not found")

    # User can view if they are the customer.
    is_customer = job.customer_id == current_user_id

    # User can view if they are the assigned worker.
    # We compare the worker's user_id through the assignment.
    from backend.app.models.worker import Worker

    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .first()
    )

    is_worker = (
        worker is not None
        and worker.user_id == current_user_id
    )

    if not is_customer and not is_worker:
        raise PermissionDeniedException(
            "You are not allowed to view this confirmation"
        )

    return confirmation