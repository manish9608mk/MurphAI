from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db
from backend.app.core.security import get_current_user_id

from backend.app.schemas.evidence import (
    EvidenceCreate,
    EvidenceResponse,
)

from backend.app.services.evidence_service import (
    create_evidence,
    get_evidence,
    get_evidence_for_work,
)


router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"],
)


# ============================================================
# Create Evidence
# ============================================================

@router.post(
    "/",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_evidence(
    data: EvidenceCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Add evidence to a Work record.

    Only the assigned worker can add evidence.
    """

    return create_evidence(
        db=db,
        work_id=data.work_id,
        evidence_type=data.evidence_type,
        description=data.description,
        url=data.url,
        current_user_id=current_user_id,
    )


# ============================================================
# Get Evidence
# ============================================================
@router.get(
    "/work/{work_id}",
    response_model=list[EvidenceResponse],
)
def get_work_evidence(
    work_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get all evidence belonging to a Work record.

    Both the customer and assigned worker can view it.
    """

    return get_evidence_for_work(
        db=db,
        work_id=work_id,
        current_user_id=current_user_id,
    )

@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def get_single_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get a single evidence record.

    Both the customer and assigned worker can view it.
    """

    return get_evidence(
        db=db,
        evidence_id=evidence_id,
        current_user_id=current_user_id,
    )