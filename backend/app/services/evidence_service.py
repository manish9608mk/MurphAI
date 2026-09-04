from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    AssignmentNotFoundException,
    PermissionDeniedException,
)
from backend.app.models.assignment import Assignment
from backend.app.models.evidence import Evidence
from backend.app.models.worker import Worker
from backend.app.models.work import Work
from backend.app.models.job import Job


def create_evidence(
    db: Session,
    work_id: int,
    evidence_type: str,
    description: str | None,
    url: str,
    current_user_id: int,
):
    """
    Create evidence for a Work record.

    Only the worker assigned to the Work can add evidence.
    """

    # --------------------------------------------------------
    # 1. Find the Work
    # --------------------------------------------------------

    work = db.query(Work).filter(Work.id == work_id).first()

    if not work:
        raise PermissionDeniedException("Work not found")

    # --------------------------------------------------------
    # 2. Find the Assignment
    # --------------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == work.assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 3. Find the assigned Worker
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .first()
    )

    if not worker:
        raise PermissionDeniedException("Assigned worker not found")

    # --------------------------------------------------------
    # 4. Check ownership
    # --------------------------------------------------------

    if worker.user_id != current_user_id:
        raise PermissionDeniedException(
            "You are not allowed to add evidence to this work"
        )

    # --------------------------------------------------------
    # 5. Evidence can only be added after work starts
    # --------------------------------------------------------

    if work.status not in {"in_progress", "completed"}:
        raise PermissionDeniedException(
            "Evidence can only be added when work is in progress or completed"
        )

    # --------------------------------------------------------
    # 6. Validate evidence type
    # --------------------------------------------------------

    allowed_types = {
        "photo",
        "document",
        "video",
        "receipt",
        "other",
    }

    if evidence_type not in allowed_types:
        raise PermissionDeniedException(
            f"Invalid evidence type: {evidence_type}"
        )

    # --------------------------------------------------------
    # 7. Create evidence
    # --------------------------------------------------------

    evidence = Evidence(
        work_id=work_id,
        evidence_type=evidence_type,
        description=description,
        url=url,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


def get_evidence(
    db: Session,
    evidence_id: int,
    current_user_id: int,
):
    """
    Get evidence.

    Both the customer and assigned worker can view it.
    """

    # --------------------------------------------------------
    # 1. Find evidence
    # --------------------------------------------------------

    evidence = (
        db.query(Evidence)
        .filter(Evidence.id == evidence_id)
        .first()
    )

    if not evidence:
        raise PermissionDeniedException("Evidence not found")

    # --------------------------------------------------------
    # 2. Find Work
    # --------------------------------------------------------

    work = (
        db.query(Work)
        .filter(Work.id == evidence.work_id)
        .first()
    )

    if not work:
        raise PermissionDeniedException("Work not found")

    # --------------------------------------------------------
    # 3. Find Assignment
    # --------------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == work.assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 4. Find Job and Worker
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 5. Check access
    # --------------------------------------------------------

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
            "You are not allowed to view this evidence"
        )

    return evidence