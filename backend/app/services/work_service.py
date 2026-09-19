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
    WorkerNotFoundException,
)


def create_work(
    db: Session,
    assignment_id: int,
    description: str | None,
    current_user_id: int,
):
    """
    Create a Work record for an accepted assignment.

    Only the assigned worker can create the work.
    """

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .with_for_update()
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    if assignment.status != "accepted":
        raise PermissionDeniedException(
            "Work can only be created for an accepted assignment"
        )

    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to create work for this assignment"
        )

    existing_work = (
        db.query(Work)
        .filter(Work.assignment_id == assignment_id)
        .first()
    )

    if existing_work:
        raise PermissionDeniedException(
            "Work already exists for this assignment"
        )

    work = Work(
        assignment_id=assignment_id,
        status="pending",
        description=description,
    )

    db.add(work)
    db.commit()
    db.refresh(work)

    return work


def get_work(
    db: Session,
    work_id: int,
    current_user_id: int,
):
    """
    Get a Work record for the Job owner or assigned Worker.
    """

    work = (
        db.query(Work)
        .filter(Work.id == work_id)
        .first()
    )

    if not work:
        raise PermissionDeniedException(
            "Work not found"
        )

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == work.assignment_id)
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
            "You are not allowed to view this work"
        )

    return work


def get_work_for_assignment(
    db: Session,
    assignment_id: int,
    current_user_id: int,
):
    """
    Get the single Work record connected to an assignment.
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
            "You are not allowed to view work for this assignment"
        )

    work = (
        db.query(Work)
        .filter(Work.assignment_id == assignment_id)
        .first()
    )

    if not work:
        raise PermissionDeniedException(
            "Work not found for this assignment"
        )

    return work


def get_my_works(
    db: Session,
    current_user_id: int,
):
    """
    Return Work records belonging to the authenticated worker.
    """

    worker = (
        db.query(Worker)
        .filter(Worker.user_id == current_user_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    rows = (
        db.query(Work, Assignment, Job)
        .join(
            Assignment,
            Work.assignment_id == Assignment.id,
        )
        .join(
            Job,
            Assignment.job_id == Job.id,
        )
        .filter(
            Assignment.worker_id == worker.id,
        )
        .order_by(
            Work.created_at.desc(),
        )
        .all()
    )

    return [
        {
            "id": work.id,
            "assignment_id": work.assignment_id,
            "status": work.status,
            "description": work.description,
            "started_at": work.started_at,
            "completed_at": work.completed_at,
            "created_at": work.created_at,
            "updated_at": work.updated_at,
            "job_title": job.title,
            "job_description": job.description,
            "location": job.location,
            "budget": job.budget,
            "job_status": job.status,
        }
        for work, assignment, job in rows
    ]


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

    work = (
        db.query(Work)
        .filter(Work.id == work_id)
        .first()
    )

    if not work:
        raise PermissionDeniedException(
            "Work not found"
        )

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == work.assignment_id)
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
        raise WorkerNotFoundException()

    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to update this work"
        )

    if work.status == "completed":
        raise PermissionDeniedException(
            "Completed work cannot be modified"
        )

    work.description = description

    db.commit()
    db.refresh(work)

    return work


def update_work_status(
    db: Session,
    work_id: int,
    new_status: str,
    current_user_id: int,
):
    """
    Change the status of Work.

    Allowed flow:

        pending -> in_progress -> completed
    """

    work = (
        db.query(Work)
        .filter(Work.id == work_id)
        .first()
    )

    if not work:
        raise PermissionDeniedException(
            "Work not found"
        )

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == work.assignment_id)
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
        raise WorkerNotFoundException()

    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to change this work status"
        )

    allowed_statuses = {
        "pending",
        "in_progress",
        "completed",
    }

    if new_status not in allowed_statuses:
        raise PermissionDeniedException(
            f"Invalid work status: {new_status}"
        )

    valid_transitions = {
        "pending": {"in_progress"},
        "in_progress": {"completed"},
        "completed": set(),
    }

    current_status = work.status

    if new_status not in valid_transitions[current_status]:
        raise PermissionDeniedException(
            f"Invalid work status transition: "
            f"{current_status} -> {new_status}"
        )

    if new_status == "in_progress":
        work.started_at = datetime.now(timezone.utc)

    if new_status == "completed":
        work.completed_at = datetime.now(timezone.utc)

    work.status = new_status

    job = (
        db.query(Job)
        .filter(Job.id == assignment.job_id)
        .first()
    )

    if job:
        if new_status == "in_progress":
            job.status = "in_progress"
        elif new_status == "completed":
            job.status = "completed"

    db.commit()
    db.refresh(work)

    return work
