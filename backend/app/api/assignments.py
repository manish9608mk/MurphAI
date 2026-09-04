from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db
from backend.app.core.security import get_current_user_id

from backend.app.schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
)

from backend.app.services.assignment_service import (
    create_assignment,
    get_assignment,
    accept_assignment,
    reject_assignment,
    cancel_assignment,
)


router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"],
)


@router.post(
    "/",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_assignment(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Customer creates a worker assignment.
    """

    return create_assignment(
        db,
        assignment_data.job_id,
        assignment_data.worker_id,
        current_user_id,
    )


@router.get(
    "/{assignment_id}",
    response_model=AssignmentResponse,
)
def get_single_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Customer or assigned worker views an assignment.
    """

    return get_assignment(
        db,
        assignment_id,
        current_user_id,
    )


@router.patch(
    "/{assignment_id}/accept",
    response_model=AssignmentResponse,
)
def accept_single_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Assigned worker accepts the assignment.
    """

    return accept_assignment(
        db,
        assignment_id,
        current_user_id,
    )


@router.patch(
    "/{assignment_id}/reject",
    response_model=AssignmentResponse,
)
def reject_single_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Assigned worker rejects the assignment.
    """

    return reject_assignment(
        db,
        assignment_id,
        current_user_id,
    )


@router.patch(
    "/{assignment_id}/cancel",
    response_model=AssignmentResponse,
)
def cancel_single_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Customer cancels the assignment.
    """

    return cancel_assignment(
        db,
        assignment_id,
        current_user_id,
    )