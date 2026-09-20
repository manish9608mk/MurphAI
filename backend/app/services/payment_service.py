# Payment Services

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.core.exceptions import (
    AssignmentNotFoundException,
    PermissionDeniedException,
)

from backend.app.models.assignment import Assignment
from backend.app.models.confirmation import Confirmation
from backend.app.models.job import Job
from backend.app.models.payment import Payment
from backend.app.models.worker import Worker
from backend.app.models.work import Work


def create_payment(
    db: Session,
    work_id: int,
    transaction_reference: str | None,
    current_user_id: int,
):
    """
    Create a payment record for confirmed work.

    The Work row is locked before checking for an existing
    payment so concurrent payment creation requests for the
    same work are serialized.

    The payment amount is determined by the backend
    from the Job budget.
    """

    # Lock the Work row for this transaction.
    work = (
        db.query(Work)
        .filter(Work.id == work_id)
        .with_for_update()
        .first()
    )

    if not work:
        raise PermissionDeniedException(
            "Work not found"
        )

    # Payment requires completed Work.
    if work.status != "completed":
        raise PermissionDeniedException(
            "Payment can only be created for completed work"
        )

    # Find Assignment.
    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.id == work.assignment_id
        )
        .first()
    )

    if not assignment:
        raise AssignmentNotFoundException()

    # Find Job.
    job = (
        db.query(Job)
        .filter(Job.id == assignment.job_id)
        .first()
    )

    if not job:
        raise PermissionDeniedException(
            "Job not found"
        )

    # Only the Job owner can create the payment.
    if job.customer_id != current_user_id:
        raise PermissionDeniedException(
            "Only the customer can create this payment"
        )

    # Payment requires customer confirmation.
    confirmation = (
        db.query(Confirmation)
        .filter(
            Confirmation.work_id == work_id
        )
        .first()
    )

    if not confirmation:
        raise PermissionDeniedException(
            "Work must be confirmed before payment"
        )

    # Check for an existing payment while holding the
    # Work row lock.
    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.work_id == work_id
        )
        .first()
    )

    if existing_payment:
        raise PermissionDeniedException(
            "Payment already exists for this work"
        )

    # Find assigned worker.
    worker = (
        db.query(Worker)
        .filter(
            Worker.id == assignment.worker_id
        )
        .first()
    )

    if not worker:
        raise PermissionDeniedException(
            "Assigned worker not found"
        )

    # The backend determines the payment amount.
    # The client cannot override the Job budget.
    payment = Payment(
        work_id=work_id,
        customer_id=current_user_id,
        worker_id=worker.id,
        amount=job.budget,
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

    The Payment row is locked before checking its state so
    concurrent paid requests cannot both transition the same
    payment from pending to paid.

    This currently simulates successful payment processing.

    A real payment-provider webhook will be responsible
    for confirming payments in a future production version.
    """

    # Lock the Payment row for this transaction.
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id
        )
        .with_for_update()
        .first()
    )

    if not payment:
        raise PermissionDeniedException(
            "Payment not found"
        )

    # Only the customer can mark it as paid.
    if payment.customer_id != current_user_id:
        raise PermissionDeniedException(
            "Only the customer can complete this payment"
        )

    # Re-check the state while holding the row lock.
    if payment.status == "paid":
        raise PermissionDeniedException(
            "Payment is already marked as paid"
        )

    # Only pending payments can become paid.
    if payment.status != "pending":
        raise PermissionDeniedException(
            f"Invalid payment status transition: "
            f"{payment.status} -> paid"
        )

    # Mark payment as paid.
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

    # Find payment.
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id
        )
        .first()
    )

    if not payment:
        raise PermissionDeniedException(
            "Payment not found"
        )

    # Customer access.
    is_customer = (
        payment.customer_id == current_user_id
    )

    # Worker access.
    worker = (
        db.query(Worker)
        .filter(
            Worker.id == payment.worker_id
        )
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

def get_payment_for_work(
    db: Session,
    work_id: int,
    current_user_id: int,
):
    """
    Get the payment connected to a Work record.

    Only the customer or assigned worker can view it.
    """

    payment = (
        db.query(Payment)
        .filter(
            Payment.work_id == work_id
        )
        .first()
    )

    if not payment:
        raise PermissionDeniedException(
            "Payment not found"
        )

    is_customer = (
        payment.customer_id == current_user_id
    )

    worker = (
        db.query(Worker)
        .filter(
            Worker.id == payment.worker_id
        )
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