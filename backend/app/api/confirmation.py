from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db
from backend.app.core.security import get_current_user_id

from backend.app.schemas.confirmation import (
    ConfirmationCreate,
    ConfirmationResponse,
)

from backend.app.services.confirmation_service import (
    create_confirmation,
    get_confirmation,
)


router = APIRouter(
    prefix="/confirmations",
    tags=["Confirmations"],
)


# ============================================================
# Create Confirmation
# ============================================================

@router.post(
    "/",
    response_model=ConfirmationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_confirmation(
    data: ConfirmationCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Customer confirms completed Work.
    """

    return create_confirmation(
        db=db,
        work_id=data.work_id,
        comment=data.comment,
        current_user_id=current_user_id,
    )


# ============================================================
# Get Confirmation
# ============================================================

@router.get(
    "/{confirmation_id}",
    response_model=ConfirmationResponse,
)
def get_single_confirmation(
    confirmation_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get a confirmation.

    The customer and assigned worker can view it.
    """

    return get_confirmation(
        db=db,
        confirmation_id=confirmation_id,
        current_user_id=current_user_id,
    )