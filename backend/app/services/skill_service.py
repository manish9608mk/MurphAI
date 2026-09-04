from sqlalchemy.orm import Session

from backend.app.models.skill import Skill, worker_skills
from backend.app.models.worker import Worker
from backend.app.schemas.skill import SkillCreate

from backend.app.core.exceptions import (
    WorkerNotFoundException,
    WorkerSkillAlreadyExistsException,
    WorkerSkillNotFoundException,
)


def normalize_skill_name(name: str) -> str:
    """
    Convert a skill name into a standard format.

    Example:

    "  Electrician  "
        ↓
    "electrician"
    """

    return " ".join(name.strip().lower().split())


def get_or_create_skill(
    db: Session,
    skill_data: SkillCreate,
):
    """
    Find an existing skill.

    If it does not exist, create it.
    """

    normalized_name = normalize_skill_name(
        skill_data.name
    )

    skill = (
        db.query(Skill)
        .filter(
            Skill.normalized_name == normalized_name
        )
        .first()
    )

    if skill:
        return skill

    skill = Skill(
        name=skill_data.name.strip(),
        normalized_name=normalized_name,
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    return skill


def get_worker_skills(
    db: Session,
    worker_id: int,
):
    """
    Return all skills belonging to a worker.
    """

    worker = (
        db.query(Worker)
        .filter(Worker.id == worker_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    return (
        db.query(Skill)
        .join(
            worker_skills,
            Skill.id == worker_skills.c.skill_id,
        )
        .filter(
            worker_skills.c.worker_id == worker_id
        )
        .all()
    )


def add_worker_skill(
    db: Session,
    worker_id: int,
    skill_data: SkillCreate,
):
    """
    Add a skill to a worker.
    """

    worker = (
        db.query(Worker)
        .filter(Worker.id == worker_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    skill = get_or_create_skill(
        db,
        skill_data,
    )

    existing_skill = (
        db.query(worker_skills)
        .filter(
            worker_skills.c.worker_id == worker_id,
            worker_skills.c.skill_id == skill.id,
        )
        .first()
    )

    if existing_skill:
        raise WorkerSkillAlreadyExistsException()

    db.execute(
        worker_skills.insert().values(
            worker_id=worker_id,
            skill_id=skill.id,
        )
    )

    db.commit()

    return skill


def remove_worker_skill(
    db: Session,
    worker_id: int,
    skill_id: int,
):
    """
    Remove a skill from a worker.
    """

    worker = (
        db.query(Worker)
        .filter(Worker.id == worker_id)
        .first()
    )

    if not worker:
        raise WorkerNotFoundException()

    existing_skill = (
        db.query(worker_skills)
        .filter(
            worker_skills.c.worker_id == worker_id,
            worker_skills.c.skill_id == skill_id,
        )
        .first()
    )

    if not existing_skill:
        raise WorkerSkillNotFoundException()

    db.execute(
        worker_skills.delete().where(
            worker_skills.c.worker_id == worker_id,
            worker_skills.c.skill_id == skill_id,
        )
    )

    db.commit()