from sqlalchemy.orm import Session

from backend.app.core.exceptions import WorkerNotFoundException
from backend.app.models.assignment import Assignment
from backend.app.models.confirmation import Confirmation
from backend.app.models.evidence import Evidence
from backend.app.models.job import Job
from backend.app.models.payment import Payment
from backend.app.models.reputation import Reputation
from backend.app.models.worker import Worker
from backend.app.models.work import Work


def get_my_verified_history(
    db: Session,
    current_user_id: int,
):
    """
    Return verified professional history for the
    authenticated worker.

    A Work record is considered verified when:

        Work.status == "completed"
        +
        Customer confirmation exists
        +
        Payment.status == "paid"

    Reputation is included when it exists, but it is
    not required for the work to appear in verified history.
    """

    # --------------------------------------------------------
    # 1. Find the worker profile belonging to the user.
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(Worker.user_id == current_user_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    # --------------------------------------------------------
    # 2. Find completed, confirmed and paid work.
    # --------------------------------------------------------

    rows = (
        db.query(
            Work,
            Assignment,
            Job,
            Confirmation,
            Payment,
        )
        .join(
            Assignment,
            Assignment.id == Work.assignment_id,
        )
        .join(
            Job,
            Job.id == Assignment.job_id,
        )
        .join(
            Confirmation,
            Confirmation.work_id == Work.id,
        )
        .join(
            Payment,
            Payment.work_id == Work.id,
        )
        .filter(
            Assignment.worker_id == worker.id,
            Work.status == "completed",
            Payment.status == "paid",
        )
        .order_by(
            Work.completed_at.desc(),
            Work.id.desc(),
        )
        .all()
    )

    history = []
    ratings = []

    # --------------------------------------------------------
    # 3. Build the verified history response.
    # --------------------------------------------------------

    for (
        work,
        assignment,
        job,
        confirmation,
        payment,
    ) in rows:

        evidence = (
            db.query(Evidence)
            .filter(
                Evidence.work_id == work.id,
            )
            .order_by(
                Evidence.created_at.asc(),
                Evidence.id.asc(),
            )
            .all()
        )

        reputation = (
            db.query(Reputation)
            .filter(
                Reputation.work_id == work.id,
            )
            .first()
        )

        if reputation:
            ratings.append(reputation.rating)

        history.append(
            {
                "work_id": work.id,
                "assignment_id": assignment.id,

                "job_id": job.id,
                "job_title": job.title,
                "job_description": job.description,
                "location": job.location,
                "budget": job.budget,
                "job_status": job.status,

                "work_description": work.description,
                "started_at": work.started_at,
                "completed_at": work.completed_at,

                "evidence": evidence,

                "confirmation": confirmation,
                "payment": payment,
                "reputation": reputation,
            }
        )

    # --------------------------------------------------------
    # 4. Calculate rating summary.
    # --------------------------------------------------------

    average_rating = None

    if ratings:
        average_rating = round(
            sum(ratings) / len(ratings),
            2,
        )

    return {
        "worker_id": worker.id,
        "total_verified_works": len(history),
        "average_rating": average_rating,
        "works": history,
    }
