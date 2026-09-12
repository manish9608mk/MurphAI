# Payment API

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_db
from backend.app.core.security import get_current_user_id

from backend.app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
)

from backend.app.services.payment_service import (
    create_payment,
    mark_payment_as_paid,
    get_payment,
)


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Customer creates a payment record
    for confirmed completed work.

    The payment amount is calculated by the backend
    from the Job budget. The client cannot choose it.
    """

    return create_payment(
        db=db,
        work_id=data.work_id,
        transaction_reference=data.transaction_reference,
        current_user_id=current_user_id,
    )


@router.patch(
    "/{payment_id}/paid",
    response_model=PaymentResponse,
)
def complete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Simulate successful payment completion.

    A real payment provider webhook will replace
    this mechanism later.
    """

    return mark_payment_as_paid(
        db=db,
        payment_id=payment_id,
        current_user_id=current_user_id,
    )


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def get_single_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get payment details.

    Only the customer or assigned worker
    can view the payment.
    """

    return get_payment(
        db=db,
        payment_id=payment_id,
        current_user_id=current_user_id,
    )