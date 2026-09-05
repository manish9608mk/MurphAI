from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db
from backend.app.core.security import get_current_user_id
from backend.app.schemas.reputation import (
    ReputationCreate,
    ReputationResponse,
)
from backend.app.services.reputation_service import (
    create_reputation,
    get_reputation,
)


router = APIRouter(
    prefix="/reputations",
    tags=["Reputations"],
)


@router.post(
    "/",
    response_model=ReputationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_reputation(
    data: ReputationCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return create_reputation(
        db=db,
        work_id=data.work_id,
        rating=data.rating,
        comment=data.comment,
        current_user_id=current_user_id,
    )


@router.get(
    "/{reputation_id}",
    response_model=ReputationResponse,
)
def get_single_reputation(
    reputation_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return get_reputation(
        db=db,
        reputation_id=reputation_id,
        current_user_id=current_user_id,
    )