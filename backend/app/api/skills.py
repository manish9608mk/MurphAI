from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from backend.app.core.dependencies import (
    get_db,
    verify_worker_access,
)

from backend.app.core.security import (
    get_current_user_id,
)

from backend.app.schemas.skill import (
    SkillCreate,
    SkillResponse,
)

from backend.app.services.skill_service import (
    add_worker_skill,
    get_worker_skills,
    remove_worker_skill,
)


router = APIRouter(
    prefix="/workers",
    tags=["Worker Skills"],
)


@router.get(
    "/{worker_id}/skills",
    response_model=list[SkillResponse],
)
def get_skills_for_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        get_current_user_id
    ),
):
    """
    Anyone authenticated can view
    a worker's skills.
    """

    return get_worker_skills(
        db,
        worker_id,
    )


@router.post(
    "/{worker_id}/skills",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_skill_to_worker(
    worker_id: int,
    skill_data: SkillCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        verify_worker_access("add skills to")
    ),
):
    """
    Worker owner can add a skill.
    """

    return add_worker_skill(
        db,
        worker_id,
        skill_data,
    )


@router.delete(
    "/{worker_id}/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_worker_skill(
    worker_id: int,
    skill_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        verify_worker_access("remove skills from")
    ),
):
    """
    Worker owner can remove a skill.
    """

    remove_worker_skill(
        db,
        worker_id,
        skill_id,
    )