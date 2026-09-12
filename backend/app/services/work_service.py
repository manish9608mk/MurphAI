# Work Service

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.models.assignment import Assignment
from backend.app.models.job import Job
from backend.app.models.worker import Worker
from backend.app.models.work import Work

from backend.app.core.exceptions import (
    AssignmentNotFoundException,
    PermissionDeniedException,
)


# ============================================================
# Create Work
# ============================================================

def create_work(
    db: Session,
    assignment_id: int,
    description: str | None,
    current_user_id: int,
):
    """
    Create a Work record for an accepted assignment.

    Only the assigned worker can create the work.

    Example:

        Assignment #7
              ↓
        Worker #5
              ↓
        Work #3
    """

    # --------------------------------------------------------
    # 1. Find the assignment
    # --------------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.id == assignment_id
        )
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 2. Assignment must be accepted
    # --------------------------------------------------------

    if assignment.status != "accepted":
        raise PermissionDeniedException(
            "Work can only be created for an accepted assignment"
        )

    # --------------------------------------------------------
    # 3. Find the worker
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(
            Worker.id == assignment.worker_id
        )
        .first()
    )

    if not worker:
        raise PermissionDeniedException(
            "Assigned worker not found"
        )

    # --------------------------------------------------------
    # 4. Only the assigned worker can create Work
    # --------------------------------------------------------

    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to create work for this assignment"
        )

    # --------------------------------------------------------
    # 5. Prevent duplicate Work records
    # --------------------------------------------------------

    existing_work = (
        db.query(Work)
        .filter(
            Work.assignment_id == assignment_id
        )
        .first()
    )

    if existing_work:
        raise PermissionDeniedException(
            "Work already exists for this assignment"
        )

    # --------------------------------------------------------
    # 6. Create Work
    # --------------------------------------------------------

    work = Work(
        assignment_id=assignment_id,
        status="pending",
        description=description,
    )

    db.add(work)
    db.commit()
    db.refresh(work)

    return work


# ============================================================
# Get Work
# ============================================================

def get_work(
    db: Session,
    work_id: int,
    current_user_id: int,
):
    """
    Get a Work record.

    Both parties can view it:

        Customer → owns the Job
        Worker   → owns the Worker profile
    """

    # --------------------------------------------------------
    # 1. Find Work
    # --------------------------------------------------------

    work = (
        db.query(Work)
        .filter(
            Work.id == work_id
        )
        .first()
    )

    if not work:
        raise PermissionDeniedException(
            "Work not found"
        )

    # --------------------------------------------------------
    # 2. Find Assignment
    # --------------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.id == work.assignment_id
        )
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 3. Find Job
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == assignment.job_id
        )
        .first()
    )

    # --------------------------------------------------------
    # 4. Find Worker
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(
            Worker.id == assignment.worker_id
        )
        .first()
    )

    # --------------------------------------------------------
    # 5. Check Customer access
    # --------------------------------------------------------

    is_customer = (
        job is not None
        and job.customer_id == current_user_id
    )

    # --------------------------------------------------------
    # 6. Check Worker access
    # --------------------------------------------------------

    is_worker = (
        worker is not None
        and worker.user_id == current_user_id
    )

    # --------------------------------------------------------
    # 7. Reject unrelated users
    # --------------------------------------------------------

    if not is_customer and not is_worker:
        raise PermissionDeniedException(
            "You are not allowed to view this work"
        )

    return work


# ============================================================
# Update Work Description
# ============================================================

def update_work(
    db: Session,
    work_id: int,
    description: str | None,
    current_user_id: int,
):
    """
    Update the description of Work.

    Only the assigned worker can update it.
    """

    # --------------------------------------------------------
    # 1. Find Work
    # --------------------------------------------------------

    work = (
        db.query(Work)
        .filter(
            Work.id == work_id
        )
        .first()
    )

    if not work:
        raise PermissionDeniedException(
            "Work not found"
        )

    # --------------------------------------------------------
    # 2. Find Assignment
    # --------------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.id == work.assignment_id
        )
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 3. Find Worker
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(
            Worker.id == assignment.worker_id
        )
        .first()
    )

    if not worker:
        raise PermissionDeniedException(
            "Assigned worker not found"
        )

    # --------------------------------------------------------
    # 4. Only assigned worker can update
    # --------------------------------------------------------

    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to update this work"
        )

    # --------------------------------------------------------
    # 5. Work cannot be changed after completion
    # --------------------------------------------------------

    if work.status == "completed":
        raise PermissionDeniedException(
            "Completed work cannot be modified"
        )

    # --------------------------------------------------------
    # 6. Update description
    # --------------------------------------------------------

    work.description = description

    db.commit()
    db.refresh(work)

    return work


# ============================================================
# Change Work Status
# ============================================================

def update_work_status(
    db: Session,
    work_id: int,
    new_status: str,
    current_user_id: int,
):
    """
    Change the status of Work.

    Allowed flow:

        pending
           ↓
      in_progress
           ↓
       completed
    """

    # --------------------------------------------------------
    # 1. Find Work
    # --------------------------------------------------------

    work = (
        db.query(Work)
        .filter(
            Work.id == work_id
        )
        .first()
    )

    if not work:
        raise PermissionDeniedException(
            "Work not found"
        )

    # --------------------------------------------------------
    # 2. Find Assignment
    # --------------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.id == work.assignment_id
        )
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 3. Find Worker
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(
            Worker.id == assignment.worker_id
        )
        .first()
    )

    if not worker:
        raise PermissionDeniedException(
            "Assigned worker not found"
        )

    # --------------------------------------------------------
    # 4. Only assigned worker can change status
    # --------------------------------------------------------

    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to change this work status"
        )

    # --------------------------------------------------------
    # 5. Validate the new status
    # --------------------------------------------------------

    allowed_statuses = {
        "pending",
        "in_progress",
        "completed",
    }

    if new_status not in allowed_statuses:
        raise PermissionDeniedException(
            f"Invalid work status: {new_status}"
        )

    # --------------------------------------------------------
    # 6. Define valid transitions
    # --------------------------------------------------------

    valid_transitions = {
        "pending": {
            "in_progress",
        },
        "in_progress": {
            "completed",
        },
        "completed": set(),
    }

    current_status = work.status

    # --------------------------------------------------------
    # 7. Check whether transition is allowed
    # --------------------------------------------------------

    if new_status not in valid_transitions[current_status]:
        raise PermissionDeniedException(
            f"Invalid work status transition: "
            f"{current_status} -> {new_status}"
        )

    # --------------------------------------------------------
    # 8. Update timestamps
    # --------------------------------------------------------

    if new_status == "in_progress":
        work.started_at = datetime.now(timezone.utc)

    if new_status == "completed":
        work.completed_at = datetime.now(timezone.utc)

    # --------------------------------------------------------
    # 9. Update status
    # --------------------------------------------------------

    work.status = new_status

    # --------------------------------------------------------
    # 10. Keep the Job lifecycle synchronized
    # --------------------------------------------------------

    job = (
        db.query(Job)
        .filter(
            Job.id == assignment.job_id
        )
        .first()
    )

    if job:

        # Work started.
        if new_status == "in_progress":
            job.status = "in_progress"

        # Work completed.
        elif new_status == "completed":
            job.status = "completed"

    # --------------------------------------------------------
    # 11. Save changes
    # --------------------------------------------------------

    db.commit()
    db.refresh(work)

    return work