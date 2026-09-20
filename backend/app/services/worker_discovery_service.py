from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models.assignment import Assignment
from backend.app.models.confirmation import Confirmation
from backend.app.models.payment import Payment
from backend.app.models.reputation import Reputation
from backend.app.models.skill import Skill, worker_skills
from backend.app.models.user import User
from backend.app.models.worker import Worker
from backend.app.models.work import Work


def discover_workers(
    db: Session,
    current_user_id: int,
    search: str | None = None,
    location: str | None = None,
    skill: str | None = None,
    available_only: bool = False,
    limit: int = 50,
    offset: int = 0,
):
    """
    Return public-safe workers for customer discovery.

    Verified work requires:

        completed Work
        +
        customer confirmation
        +
        paid Payment
    """

    query = (
        db.query(Worker)
        .join(User, User.id == Worker.user_id)
        .filter(Worker.user_id != current_user_id)
    )

    if search:
        search_term = f"%{search.strip()}%"

        query = query.filter(
            (User.name.ilike(search_term))
            | (Worker.bio.ilike(search_term))
            | (Worker.location.ilike(search_term))
        )

    if location:
        query = query.filter(
            Worker.location.ilike(
                f"%{location.strip()}%",
            )
        )

    if skill:
        query = (
            query
            .join(
                worker_skills,
                Worker.id == worker_skills.c.worker_id,
            )
            .join(
                Skill,
                Skill.id == worker_skills.c.skill_id,
            )
            .filter(
                Skill.name.ilike(
                    f"%{skill.strip()}%",
                )
            )
        )

    if available_only:
        query = query.filter(
            Worker.is_available.is_(True),
        )

    total = (
        query
        .with_entities(
            func.count(
                func.distinct(Worker.id),
            ),
        )
        .scalar()
        or 0
    )

    workers = (
        query
        .distinct()
        .order_by(
            Worker.is_available.desc(),
            Worker.updated_at.desc(),
            Worker.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    if not workers:
        return {
            "total": total,
            "workers": [],
        }

    worker_ids = [worker.id for worker in workers]

    skill_rows = (
        db.query(
            worker_skills.c.worker_id,
            Skill.name,
        )
        .join(
            Skill,
            Skill.id == worker_skills.c.skill_id,
        )
        .filter(
            worker_skills.c.worker_id.in_(worker_ids),
        )
        .order_by(
            Skill.name.asc(),
        )
        .all()
    )

    skills_by_worker = {
        worker_id: []
        for worker_id in worker_ids
    }

    for worker_id, skill_name in skill_rows:
        skills_by_worker[worker_id].append(
            skill_name,
        )

    verified_rows = (
        db.query(
            Assignment.worker_id,
            func.count(
                func.distinct(Work.id),
            ).label("verified_work_count"),
            func.avg(
                Reputation.rating,
            ).label("average_rating"),
        )
        .join(
            Work,
            Work.assignment_id == Assignment.id,
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
            Assignment.worker_id.in_(worker_ids),
            Work.status == "completed",
            Payment.status == "paid",
        )
        .group_by(
            Assignment.worker_id,
        )
        .all()
    )

    verified_by_worker = {
        worker_id: {
            "verified_work_count": verified_work_count,
            "average_rating": (
                round(float(average_rating), 2)
                if average_rating is not None
                else None
            ),
        }
        for (
            worker_id,
            verified_work_count,
            average_rating,
        ) in verified_rows
    }

    user_rows = (
        db.query(
            User.id,
            User.name,
        )
        .filter(
            User.id.in_(
                [worker.user_id for worker in workers]
            ),
        )
        .all()
    )

    user_names = {
        user_id: name
        for user_id, name in user_rows
    }

    result = []

    for worker in workers:
        stats = verified_by_worker.get(
            worker.id,
            {
                "verified_work_count": 0,
                "average_rating": None,
            },
        )

        result.append(
            {
                "worker_id": worker.id,
                "name": user_names.get(
                    worker.user_id,
                    "Worker",
                ),
                "bio": worker.bio,
                "location": worker.location,
                "experience_years": worker.experience_years,
                "is_available": worker.is_available,
                "skills": skills_by_worker.get(
                    worker.id,
                    [],
                ),
                "verified_work_count": stats[
                    "verified_work_count"
                ],
                "average_rating": stats[
                    "average_rating"
                ],
            }
        )

    return {
        "total": total,
        "workers": result,
    }
