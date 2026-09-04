from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    AssignmentNotFoundException,
    PermissionDeniedException,
)
from backend.app.models.assignment import Assignment
from backend.app.models.job import Job
from backend.app.models.payment import Payment
from backend.app.models.worker import Worker
from backend.app.models.work import Work


def create_payment(
    db: Session,
    work_id: int,
    amount: float,
    transaction_reference: str | None,
    current_user_id: int,
):
    """
    Create a payment record for confirmed work.

    Only the customer who owns the job can create the payment.
    """

    # --------------------------------------------------------
    # 1. Find the Work
    # --------------------------------------------------------

    work = db.query(Work).filter(Work.id == work_id).first()

    if not work:
        raise PermissionDeniedException("Work not found")

    # Payment is only allowed after Work is completed.
    if work.status != "completed":
        raise PermissionDeniedException(
            "Payment can only be created for completed work"
        )

    # --------------------------------------------------------
    # 2. Find the Assignment
    # --------------------------------------------------------

    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == work.assignment_id)
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # --------------------------------------------------------
    # 3. Find the Job
    # --------------------------------------------------------

    job = db.query(Job).filter(Job.id == assignment.job_id).first()

    if not job:
        raise PermissionDeniedException("Job not found")

    # --------------------------------------------------------
    # 4. Only the Job customer can create payment
    # --------------------------------------------------------

    if job.customer_id != current_user_id:
        raise PermissionDeniedException(
            "Only the customer can create this payment"
        )

    # --------------------------------------------------------
    # 5. Payment requires confirmation
    # --------------------------------------------------------

    from backend.app.models.confirmation import Confirmation

    confirmation = (
        db.query(Confirmation)
        .filter(Confirmation.work_id == work_id)
        .first()
    )

    if not confirmation:
        raise PermissionDeniedException(
            "Work must be confirmed before payment"
        )

    # --------------------------------------------------------
    # 6. Prevent duplicate payment
    # --------------------------------------------------------

    existing_payment = (
        db.query(Payment)
        .filter(Payment.work_id == work_id)
        .first()
    )

    if existing_payment:
        raise PermissionDeniedException(
            "Payment already exists for this work"
        )

    # --------------------------------------------------------
    # 7. Find the assigned worker
    # --------------------------------------------------------

    worker = (
        db.query(Worker)
        .filter(Worker.id == assignment.worker_id)
        .first()
    )

    if not worker:
        raise PermissionDeniedException("Assigned worker not found")

    # --------------------------------------------------------
    # 8. Create payment
    # --------------------------------------------------------

    payment = Payment(
        work_id=work_id,
        customer_id=current_user_id,
        worker_id=worker.id,
        amount=amount,
        status="pending",
        transaction_reference=transaction_reference,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


def mark_payment_as_paid(
    db: Session,
    payment_id: int,
    current_user_id: int,
):
    """
    Mark a payment as paid.

    For now this simulates successful payment processing.

    Later, Stripe/Razorpay webhook processing will be
    responsible for confirming the payment.
    """

    # --------------------------------------------------------
    # 1. Find payment
    # --------------------------------------------------------

    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise PermissionDeniedException("Payment not found")

    # --------------------------------------------------------
    # 2. Only the customer can mark payment as paid
    # --------------------------------------------------------

    if payment.customer_id != current_user_id:
        raise PermissionDeniedException(
            "Only the customer can complete this payment"
        )

    # --------------------------------------------------------
    # 3. Prevent duplicate payment completion
    # --------------------------------------------------------

    if payment.status == "paid":
        raise PermissionDeniedException(
            "Payment is already marked as paid"
        )

    # --------------------------------------------------------
    # 4. Only pending payments can become paid
    # --------------------------------------------------------

    if payment.status != "pending":
        raise PermissionDeniedException(
            f"Invalid payment status transition: "
            f"{payment.status} -> paid"
        )

    # --------------------------------------------------------
    # 5. Mark payment as paid
    # --------------------------------------------------------

    payment.status = "paid"
    payment.paid_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(payment)

    return payment


def get_payment(
    db: Session,
    payment_id: int,
    current_user_id: int,
):
    """
    Get a payment.

    Only the customer or assigned worker can view it.
    """

    # --------------------------------------------------------
    # 1. Find payment
    # --------------------------------------------------------

    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise PermissionDeniedException("Payment not found")

    # --------------------------------------------------------
    # 2. Check access
    # --------------------------------------------------------

    is_customer = payment.customer_id == current_user_id

    worker = (
        db.query(Worker)
        .filter(Worker.id == payment.worker_id)
        .first()
    )

    is_worker = (
        worker is not None
        and worker.user_id == current_user_id
    )

    if not is_customer and not is_worker:
        raise PermissionDeniedException(
            "You are not allowed to view this payment"
        )

    return payment