from sqlalchemy.orm import Session

from backend.app.core.exceptions import WorkerNotFoundException
from backend.app.models.assignment import Assignment
from backend.app.models.confirmation import Confirmation
from backend.app.models.job import Job
from backend.app.models.payment import Payment
from backend.app.models.reputation import Reputation
from backend.app.models.skill import Skill, worker_skills
from backend.app.models.user import User
from backend.app.models.worker import Worker
from backend.app.models.work import Work


def get_worker_public_profile(
    db: Session,
    worker_id: int,
):
    """
    Return the public profile of a worker.

    Verified work is defined as:

        Work completed
        +
        Customer confirmation exists
        +
        Payment is paid

    Only public-safe worker information and customer reviews
    are returned.
    """

    # --------------------------------------------------------
    # 1. Find the worker and associated user.
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(Worker.id == worker_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    user = (
        db.query(User)
        .filter(User.id == worker.user_id)
        .first()
    )

    if not user:
        raise WorkerNotFoundException()

    # --------------------------------------------------------
    # 2. Get worker skills.
    # --------------------------------------------------------

    skills = (
        db.query(Skill.name)
        .join(
            worker_skills,
            Skill.id == worker_skills.c.skill_id,
        )
        .filter(
            worker_skills.c.worker_id == worker.id,
        )
        .order_by(
            Skill.name.asc(),
        )
        .all()
    )

    skill_names = [
        skill_name
        for (skill_name,) in skills
    ]

    # --------------------------------------------------------
    # 3. Get verified completed work and reputation.
    # --------------------------------------------------------

    verified_rows = (
        db.query(
            Work,
            Job,
            Reputation,
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
        .outerjoin(
            Reputation,
            Reputation.work_id == Work.id,
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

    ratings = []
    reviews = []

    for work, job, reputation in verified_rows:
        if reputation:
            ratings.append(reputation.rating)

            reviews.append(
                {
                    "work_id": work.id,
                    "job_title": job.title,
                    "completed_at": work.completed_at,
                    "rating": reputation.rating,
                    "comment": reputation.comment,
                }
            )

    # --------------------------------------------------------
    # 4. Calculate average rating.
    # --------------------------------------------------------

    average_rating = None

    if ratings:
        average_rating = round(
            sum(ratings) / len(ratings),
            2,
        )

    # --------------------------------------------------------
    # 5. Return public profile.
    # --------------------------------------------------------

    return {
        "worker_id": worker.id,
        "name": user.name,
        "bio": worker.bio,
        "location": worker.location,
        "experience_years": worker.experience_years,
        "is_available": worker.is_available,

        "skills": skill_names,

        "verified_work_count": len(verified_rows),
        "average_rating": average_rating,

        "reviews": reviews,
    }
