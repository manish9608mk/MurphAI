# Assignment Services

from sqlalchemy.orm import Session

from backend.app.models.assignment import Assignment
from backend.app.models.job import Job
from backend.app.models.worker import Worker

from backend.app.core.exceptions import (
    AssignmentNotFoundException,
    AssignmentAlreadyExistsException,
    InvalidAssignmentTransitionException,
    WorkerUnavailableException,
    PermissionDeniedException,
    WorkerNotFoundException,
)


def create_assignment(
    db: Session,
    job_id: int,
    worker_id: int,
    current_user_id: int,
):
    """
    Customer assigns a worker to a job.

    New assignment starts as pending.

    The Job row is locked before checking the state so that
    concurrent assignment requests cannot race on the same job.
    """

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .with_for_update()
        .first()
    )

    if not job:
        raise AssignmentNotFoundException()

    if job.customer_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to assign a worker to this job"
        )

    if job.status != "open":
        raise InvalidAssignmentTransitionException(
            "Cannot create an assignment for a job "
            f"with status: {job.status}"
        )

    worker = (
        db.query(Worker)
        .filter(Worker.id == worker_id)
        .with_for_update()
        .first()
    )

    if not worker:
        raise AssignmentNotFoundException()

    if not worker.is_available:
        raise WorkerUnavailableException()

    existing_assignment = (
        db.query(Assignment)
        .filter(
            Assignment.job_id == job_id,
            Assignment.worker_id == worker_id,
        )
        .first()
    )

    if existing_assignment:
        raise AssignmentAlreadyExistsException()

    assignment = Assignment(
        job_id=job_id,
        worker_id=worker_id,
        status="pending",
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment


def get_my_assignments(
    db: Session,
    current_user_id: int,
):
    """
    Return assignments belonging to the authenticated worker.

    The response includes the associated job summary so the worker
    can review and act on an assignment without making a separate
    job-list request for every assignment.
    """

    worker = (
        db.query(Worker)
        .filter(Worker.user_id == current_user_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    rows = (
        db.query(Assignment, Job)
        .join(
            Job,
            Assignment.job_id == Job.id,
        )
        .filter(
            Assignment.worker_id == worker.id,
        )
        .order_by(
            Assignment.created_at.desc(),
        )
        .all()
    )

    return [
        {
            "id": assignment.id,
            "job_id": assignment.job_id,
            "worker_id": assignment.worker_id,
            "status": assignment.status,
            "job_title": job.title,
            "job_description": job.description,
            "location": job.location,
            "budget": job.budget,
            "job_status": job.status,
            "created_at": assignment.created_at,
            "updated_at": assignment.updated_at,
        }
        for assignment, job in rows
    ]


def get_assignment(
    db: Session,
    assignment_id: int,
    current_user_id: int,
):
    """
    Get one assignment.

    Only these users can view it:

    1. Customer who owns the job.
    2. Worker who owns the worker profile.
    """

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    job = (
        db.query(Job)
        .filter(Job.id == assignment.job_id)
        .first()
    )

    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .first()
    )

    is_customer = (
        job is not None
        and job.customer_id == current_user_id
    )

    is_worker = (
        worker is not None
        and worker.user_id == current_user_id
    )

    if not is_customer and not is_worker:
        raise PermissionDeniedException(
            "You are not allowed to view this assignment"
        )

    return assignment


def accept_assignment(
    db: Session,
    assignment_id: int,
    current_user_id: int,
):
    """
    Worker accepts a pending assignment.

    Assignment:
        pending -> accepted

    Job:
        open -> assigned

    Worker:
        available -> unavailable

    The related Job, Worker, and Assignment rows are locked
    so concurrent acceptance requests cannot both succeed.
    """

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    job = (
        db.query(Job)
        .filter(Job.id == assignment.job_id)
        .with_for_update()
        .first()
    )

    if not job:
        raise AssignmentNotFoundException()

    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .with_for_update()
        .first()
    )

    if not worker:
        raise AssignmentNotFoundException()

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .with_for_update()
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to accept this assignment"
        )

    if not worker.is_available:
        raise WorkerUnavailableException()

    if assignment.status != "pending":
        raise InvalidAssignmentTransitionException(
            "Only pending assignments can be accepted"
        )

    if job.status != "open":
        raise InvalidAssignmentTransitionException(
            "The job is no longer open"
        )

    assignment.status = "accepted"
    worker.is_available = False
    job.status = "assigned"

    db.commit()
    db.refresh(assignment)

    return assignment


def reject_assignment(
    db: Session,
    assignment_id: int,
    current_user_id: int,
):
    """
    Worker rejects a pending assignment.

    Assignment:
        pending -> rejected
    """

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .with_for_update()
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .first()
    )

    if not worker:
        raise AssignmentNotFoundException()

    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to reject this assignment"
        )

    if assignment.status != "pending":
        raise InvalidAssignmentTransitionException(
            "Only pending assignments can be rejected"
        )

    assignment.status = "rejected"

    db.commit()
    db.refresh(assignment)

    return assignment


def cancel_assignment(
    db: Session,
    assignment_id: int,
    current_user_id: int,
):
    """
    Customer cancels a pending assignment.

    Assignment:
        pending -> cancelled

    The related Job and Assignment rows are locked to prevent
    a concurrent accept/cancel race.
    """

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    job = (
        db.query(Job)
        .filter(Job.id == assignment.job_id)
        .with_for_update()
        .first()
    )

    if not job:
        raise AssignmentNotFoundException()

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .with_for_update()
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    if job.customer_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to cancel this assignment"
        )

    if assignment.status != "pending":
        raise InvalidAssignmentTransitionException(
            "Only pending assignments can be cancelled"
        )

    assignment.status = "cancelled"

    db.commit()
    db.refresh(assignment)

    return assignment
