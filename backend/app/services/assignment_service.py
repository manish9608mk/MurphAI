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

    # Lock the Job row for this transaction.
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .with_for_update()
        .first()
    )

    if not job:
        raise AssignmentNotFoundException()

    # Only the customer who owns the job can assign a worker.
    if job.customer_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to assign a worker to this job"
        )

    # Job must still be open.
    if job.status != "open":
        raise InvalidAssignmentTransitionException(
            "Cannot create an assignment for a job "
            f"with status: {job.status}"
        )

    # Lock the Worker row before checking availability.
    worker = (
        db.query(Worker)
        .filter(Worker.id == worker_id)
        .with_for_update()
        .first()
    )

    if not worker:
        raise AssignmentNotFoundException()

    # Worker must be available.
    if not worker.is_available:
        raise WorkerUnavailableException()

    # Check for an existing assignment after acquiring the locks.
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

    # Create the pending assignment.
    assignment = Assignment(
        job_id=job_id,
        worker_id=worker_id,
        status="pending",
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment


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

    # Find the assignment first so we know its related Job and Worker.
    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # Lock the Job first.
    #
    # The Job is the shared resource that determines whether
    # another assignment can also be accepted.
    job = (
        db.query(Job)
        .filter(Job.id == assignment.job_id)
        .with_for_update()
        .first()
    )

    if not job:
        raise AssignmentNotFoundException()

    # Lock the Worker next.
    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .with_for_update()
        .first()
    )

    if not worker:
        raise AssignmentNotFoundException()

    # Lock the Assignment as well.
    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .with_for_update()
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # Only the assigned worker can accept.
    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to accept this assignment"
        )

    # Re-check the assignment state after acquiring the lock.
    if assignment.status != "pending":
        raise InvalidAssignmentTransitionException(
            "Only pending assignments can be accepted"
        )

    # Re-check the Job state after acquiring the lock.
    if job.status != "open":
        raise InvalidAssignmentTransitionException(
            "The job is no longer open"
        )

    # Perform all state changes inside the same transaction.
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

    # Lock the Assignment so two requests cannot update it
    # at the same time.
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

    # Only the assigned worker can reject.
    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to reject this assignment"
        )

    # Re-check the state while holding the lock.
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

    # Find the assignment first so we know its Job.
    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # Lock the Job first.
    job = (
        db.query(Job)
        .filter(Job.id == assignment.job_id)
        .with_for_update()
        .first()
    )

    if not job:
        raise AssignmentNotFoundException()

    # Lock the Assignment after the Job.
    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .with_for_update()
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # Only the job owner can cancel.
    if job.customer_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to cancel this assignment"
        )

    # Re-check the state while holding the lock.
    if assignment.status != "pending":
        raise InvalidAssignmentTransitionException(
            "Only pending assignments can be cancelled"
        )

    assignment.status = "cancelled"

    db.commit()
    db.refresh(assignment)

    return assignment