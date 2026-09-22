from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.schemas.user import (
    UserUpdate,
    UserResponse,
)

from backend.app.services.user_service import (
    get_user,
    update_user,
    delete_user,
)

from backend.app.core.dependencies import (
    get_db,
    verify_user_access,
)

from backend.app.core.security import get_current_user_id


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_current_user(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        get_current_user_id
    ),
):
    return get_user(
        db,
        current_user_id,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_single_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        verify_user_access("access")
    ),
):
    return get_user(
        db,
        user_id,
    )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_single_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        verify_user_access("update")
    ),
):
    return update_user(
        db,
        user_id,
        user_data,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_single_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        verify_user_access("delete")
    ),
):
    delete_user(
        db,
        user_id,
    )
