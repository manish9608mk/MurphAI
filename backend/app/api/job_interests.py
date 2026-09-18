from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import (
    get_db,
    verify_job_access,
)
from backend.app.core.security import get_current_user_id
from backend.app.schemas.job_interest import (
    JobInterestCreate,
    JobInterestResponse,
    JobInterestWorkerResponse,
)
from backend.app.services.job_interest_service import (
    create_job_interest,
    get_job_interests,
    get_my_job_interests,
    withdraw_job_interest,
)


router = APIRouter(
    prefix="/job-interests",
    tags=["Job Interests"],
)


job_router = APIRouter(
    prefix="/jobs",
    tags=["Job Interests"],
)


@router.post(
    "/",
    response_model=JobInterestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_job_interest(
    interest_data: JobInterestCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        get_current_user_id
    ),
):
    """
    Worker expresses interest in an open job.
    """

    return create_job_interest(
        db,
        interest_data.job_id,
        current_user_id,
    )


@router.get(
    "/mine",
    response_model=list[JobInterestResponse],
)
def get_my_interests(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        get_current_user_id
    ),
):
    """
    Return the authenticated worker's interests.
    """

    return get_my_job_interests(
        db,
        current_user_id,
    )


@router.patch(
    "/{interest_id}/withdraw",
    response_model=JobInterestResponse,
)
def withdraw_interest(
    interest_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        get_current_user_id
    ),
):
    """
    Worker withdraws their own pending interest.
    """

    return withdraw_job_interest(
        db,
        interest_id,
        current_user_id,
    )


@job_router.get(
    "/{job_id}/interests",
    response_model=list[JobInterestWorkerResponse],
)
def get_interests_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(
        verify_job_access("view interested workers for")
    ),
):
    """
    Job owner views workers who expressed interest.
    """

    return get_job_interests(
        db,
        job_id,
        current_user_id,
    )