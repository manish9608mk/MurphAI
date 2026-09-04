from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db
from backend.app.core.security import get_current_user_id

from backend.app.schemas.work import (
    WorkCreate,
    WorkResponse,
    WorkStatusUpdate,
    WorkUpdate,
)

from backend.app.services.work_service import (
    create_work,
    get_work,
    update_work,
    update_work_status,
)


router = APIRouter(
    prefix="/works",
    tags=["Works"],
)


# ============================================================
# Create Work
# ============================================================

@router.post(
    "/",
    response_model=WorkResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_work(
    data: WorkCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Create a Work record for an accepted assignment.

    Only the assigned worker can create the Work.
    """

    return create_work(
        db=db,
        assignment_id=data.assignment_id,
        description=data.description,
        current_user_id=current_user_id,
    )


# ============================================================
# Get Work
# ============================================================

@router.get(
    "/{work_id}",
    response_model=WorkResponse,
)
def get_single_work(
    work_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get a Work record.

    The customer and assigned worker can view it.
    """

    return get_work(
        db=db,
        work_id=work_id,
        current_user_id=current_user_id,
    )


# ============================================================
# Update Work Description
# ============================================================

@router.put(
    "/{work_id}",
    response_model=WorkResponse,
)
def update_existing_work(
    work_id: int,
    data: WorkUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Update the description of Work.

    Only the assigned worker can update it.
    """

    return update_work(
        db=db,
        work_id=work_id,
        description=data.description,
        current_user_id=current_user_id,
    )


# ============================================================
# Update Work Status
# ============================================================

@router.patch(
    "/{work_id}/status",
    response_model=WorkResponse,
)
def change_work_status(
    work_id: int,
    data: WorkStatusUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Change Work status.

    Allowed lifecycle:

        pending
            ↓
        in_progress
            ↓
        completed
    """

    return update_work_status(
        db=db,
        work_id=work_id,
        new_status=data.status,
        current_user_id=current_user_id,
    )