from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobStatusUpdate,
    JobResponse,
)

from backend.app.services.job_service import (
    create_job,
    get_jobs,
    get_available_jobs,
    get_my_jobs,
    get_job,
    update_job,
    update_job_status,
    delete_job,
)

from backend.app.core.dependencies import (
    get_db,
    verify_job_access,
)

from backend.app.core.security import get_current_user_id


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return create_job(
        db,
        job_data,
        current_user_id,
    )


@router.get(
    "/",
    response_model=list[JobResponse],
)
def get_all_jobs(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return get_jobs(db)


@router.get(
    "/available",
    response_model=list[JobResponse],
)
def get_available_jobs_for_worker(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        get_current_user_id
    ),
):
    """
    Return open jobs available in the marketplace.
    """

    return get_available_jobs(
        db,
        current_user_id,
    )

@router.get(
    "/mine",
    response_model=list[JobResponse],
)
def get_my_jobs_for_current_user(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return get_my_jobs(
        db,
        current_user_id,
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_single_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return get_job(
        db,
        job_id,
    )


@router.put(
    "/{job_id}",
    response_model=JobResponse,
)
def update_single_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        verify_job_access("update")
    ),
):
    return update_job(
        db,
        job_id,
        job_data,
    )


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_single_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        verify_job_access("delete")
    ),
):
    delete_job(
        db,
        job_id,
    )


@router.patch(
    "/{job_id}/status",
    response_model=JobResponse,
)
def update_single_job_status(
    job_id: int,
    status_data: JobStatusUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        verify_job_access("update")
    ),
):
    return update_job_status(
        db,
        job_id,
        status_data.status,
    )