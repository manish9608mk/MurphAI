from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.schemas.worker import (
    WorkerCreate,
    WorkerUpdate,
    WorkerResponse,
)

from backend.app.schemas.worker_history import (
    WorkerVerifiedHistoryResponse,
)

from backend.app.schemas.worker_profile import (
    WorkerPublicProfileResponse,
)

from backend.app.services.worker_service import (
    create_worker,
    get_workers,
    get_my_worker,
    get_worker,
    update_worker,
    delete_worker,
)

from backend.app.services.worker_history_service import (
    get_my_verified_history,
)

from backend.app.services.worker_profile_service import (
    get_worker_public_profile,
)

from backend.app.core.dependencies import (
    get_db,
    verify_worker_access,
)

from backend.app.core.security import get_current_user_id


router = APIRouter(
    prefix="/workers",
    tags=["Workers"],
)


@router.post(
    "/",
    response_model=WorkerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_worker(
    worker_data: WorkerCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return create_worker(
        db,
        worker_data,
        current_user_id,
    )


@router.get(
    "/",
    response_model=list[WorkerResponse],
)
def get_all_workers(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return get_workers(db)


@router.get(
    "/me",
    response_model=WorkerResponse,
)
def get_my_worker_profile(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return get_my_worker(
        db=db,
        user_id=current_user_id,
    )


@router.get(
    "/me/history",
    response_model=WorkerVerifiedHistoryResponse,
)
def get_my_worker_history(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Return verified professional history for the
    authenticated worker.

    Verification requires:

        completed Work
        +
        customer confirmation
        +
        paid Payment
    """

    return get_my_verified_history(
        db=db,
        current_user_id=current_user_id,
    )


@router.get(
    "/{worker_id}/profile",
    response_model=WorkerPublicProfileResponse,
)
def get_public_worker_profile(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Return public worker profile information.

    Any authenticated user can view this profile.
    Private payment and customer information is excluded.
    """

    return get_worker_public_profile(
        db=db,
        worker_id=worker_id,
    )


@router.get(
    "/{worker_id}",
    response_model=WorkerResponse,
)
def get_single_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return get_worker(
        db,
        worker_id,
    )


@router.put(
    "/{worker_id}",
    response_model=WorkerResponse,
)
def update_single_worker(
    worker_id: int,
    worker_data: WorkerUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        verify_worker_access("update")
    ),
):
    return update_worker(
        db,
        worker_id,
        worker_data,
    )


@router.delete(
    "/{worker_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_single_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        verify_worker_access("delete")
    ),
):
    delete_worker(
        db,
        worker_id,
    )
