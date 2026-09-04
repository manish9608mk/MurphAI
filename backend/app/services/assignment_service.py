from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.assignment import Assignment
from backend.app.models.job import Job
from backend.app.models.worker import Worker

from backend.app.core.exceptions import (
    AssignmentNotFoundException,
    AssignmentAlreadyExistsException,
    InvalidAssignmentTransitionException,
    WorkerUnavailableException,
)


# ============================================================
# CREATE ASSIGNMENT
# ============================================================

def create_assignment(
    db: Session,
    job_id: int,
    worker_id: int,
    current_user_id: int,
):
    """
    Customer assigns a worker to a job.

    New assignment starts with:
        pending
    """

    # --------------------------------------------------------
    # 1. Find the job
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 2. Only the customer who owns the job
    #    can assign a worker
    # --------------------------------------------------------

    if job.customer_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to assign a worker to this job",
        )

    # --------------------------------------------------------
    # 3. Job must be open
    # --------------------------------------------------------

    if job.status != "open":
        raise InvalidAssignmentTransitionException(
            "Cannot create an assignment for a job "
            f"with status: {job.status}"
        )

    # --------------------------------------------------------
    # 4. Find the worker
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(Worker.id == worker_id)
        .first()
    )

    if not worker:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 5. Worker must be available
    # --------------------------------------------------------

    if not worker.is_available:
        raise WorkerUnavailableException()

    # --------------------------------------------------------
    # 6. Prevent duplicate assignment
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 7. Create assignment
    # --------------------------------------------------------

    assignment = Assignment(
        job_id=job_id,
        worker_id=worker_id,
        status="pending",
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment


# ============================================================
# GET ASSIGNMENT
# ============================================================

def get_assignment(
    db: Session,
    assignment_id: int,
    current_user_id: int,
):
    """
    Get one assignment.

    Only these two users can see it:

    1. Customer who owns the job
    2. Worker who owns the worker profile
    """

    # --------------------------------------------------------
    # 1. Find assignment
    # --------------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 2. Find related job
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(Job.id == assignment.job_id)
        .first()
    )

    # --------------------------------------------------------
    # 3. Find related worker
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .first()
    )

    # --------------------------------------------------------
    # 4. Check if current user is the customer
    # --------------------------------------------------------

    is_customer = (
        job is not None
        and job.customer_id == current_user_id
    )

    # --------------------------------------------------------
    # 5. Check if current user owns the worker profile
    # --------------------------------------------------------

    is_worker = (
        worker is not None
        and worker.user_id == current_user_id
    )

    # --------------------------------------------------------
    # 6. User must be either customer or worker
    # --------------------------------------------------------

    if not is_customer and not is_worker:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this assignment",
        )

    return assignment


# ============================================================
# ACCEPT ASSIGNMENT
# ============================================================

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
    """

    # --------------------------------------------------------
    # 1. Find assignment
    # --------------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 2. Find worker
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .first()
    )

    if not worker:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 3. Only assigned worker can accept
    # --------------------------------------------------------

    if worker.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to accept this assignment",
        )

    # --------------------------------------------------------
    # 4. Assignment must be pending
    # --------------------------------------------------------

    if assignment.status != "pending":
        raise InvalidAssignmentTransitionException(
            "Only pending assignments can be accepted"
        )

    # --------------------------------------------------------
    # 5. Find related job
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(Job.id == assignment.job_id)
        .first()
    )

    if not job:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 6. Job must still be open
    # --------------------------------------------------------

    if job.status != "open":
        raise InvalidAssignmentTransitionException(
            "The job is no longer open"
        )

    # --------------------------------------------------------
    # 7. Accept assignment
    # --------------------------------------------------------

    assignment.status = "accepted"

    # --------------------------------------------------------
    # 8. Worker becomes unavailable
    # --------------------------------------------------------

    worker.is_available = False

    # --------------------------------------------------------
    # 9. Job becomes assigned
    # --------------------------------------------------------

    job.status = "assigned"

    db.commit()
    db.refresh(assignment)

    return assignment


# ============================================================
# REJECT ASSIGNMENT
# ============================================================

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

    # --------------------------------------------------------
    # 1. Find assignment
    # --------------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 2. Find worker
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .first()
    )

    if not worker:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 3. Only assigned worker can reject
    # --------------------------------------------------------

    if worker.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to reject this assignment",
        )

    # --------------------------------------------------------
    # 4. Assignment must be pending
    # --------------------------------------------------------

    if assignment.status != "pending":
        raise InvalidAssignmentTransitionException(
            "Only pending assignments can be rejected"
        )

    # --------------------------------------------------------
    # 5. Reject assignment
    # --------------------------------------------------------

    assignment.status = "rejected"

    db.commit()
    db.refresh(assignment)

    return assignment


# ============================================================
# CANCEL ASSIGNMENT
# ============================================================

def cancel_assignment(
    db: Session,
    assignment_id: int,
    current_user_id: int,
):
    """
    Customer cancels a pending assignment.

    Assignment:
        pending -> cancelled
    """

    # --------------------------------------------------------
    # 1. Find assignment
    # --------------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 2. Find related job
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(Job.id == assignment.job_id)
        .first()
    )

    if not job:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 3. Only job owner can cancel
    # --------------------------------------------------------

    if job.customer_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to cancel this assignment",
        )

    # --------------------------------------------------------
    # 4. Assignment must be pending
    # --------------------------------------------------------

    if assignment.status != "pending":
        raise InvalidAssignmentTransitionException(
            "Only pending assignments can be cancelled"
        )

    # --------------------------------------------------------
    # 5. Cancel assignment
    # --------------------------------------------------------

    assignment.status = "cancelled"

    db.commit()
    db.refresh(assignment)

    return assignment