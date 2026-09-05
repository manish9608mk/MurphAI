from backend.app.models.assignment import Assignment
from backend.app.models.confirmation import Confirmation
from backend.app.models.job import Job
from backend.app.models.payment import Payment
from backend.app.models.reputation import Reputation
from backend.app.models.user import User
from backend.app.models.worker import Worker
from backend.app.models.work import Work
from backend.app.core.security import hash_password


def create_user(db, name, email):
    user = User(
        name=name,
        email=email,
        password_hash=hash_password("password"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_completed_work(db, customer, worker_user):
    worker = Worker(
        user_id=worker_user.id,
        location="Bhopal",
        experience_years=5,
        is_available=False,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)

    job = Job(
        title="Electrical Repair",
        description="Repair electrical wiring",
        location="Bhopal",
        budget=1000,
        status="completed",
        customer_id=customer.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    assignment = Assignment(
        job_id=job.id,
        worker_id=worker.id,
        status="accepted",
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    work = Work(
        assignment_id=assignment.id,
        status="completed",
        description="Electrical wiring repaired",
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    confirmation = Confirmation(
        work_id=work.id,
        customer_id=customer.id,
        comment="Work completed successfully",
    )
    db.add(confirmation)
    db.commit()

    payment = Payment(
        work_id=work.id,
        customer_id=customer.id,
        worker_id=worker.id,
        amount=1000,
        status="paid",
        transaction_reference="TEST-TXN-001",
    )
    db.add(payment)
    db.commit()

    return worker, job, assignment, work


def get_token(client, email):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "password",
        },
    )
    return response.json()["access_token"]


def test_customer_can_create_reputation(client, db):
    customer = create_user(
        db,
        "Customer",
        "customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "worker@example.com",
    )

    _, _, _, work = create_completed_work(
        db,
        customer,
        worker_user,
    )

    response = client.post(
        "/reputations/",
        json={
            "work_id": work.id,
            "rating": 5,
            "comment": "Excellent work",
        },
        headers={
            "Authorization": f"Bearer {get_token(client, customer.email)}"
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["work_id"] == work.id
    assert data["customer_id"] == customer.id
    assert data["worker_id"] > 0
    assert data["rating"] == 5
    assert data["comment"] == "Excellent work"


def test_worker_cannot_create_reputation(client, db):
    customer = create_user(
        db,
        "Customer",
        "customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "worker@example.com",
    )

    _, _, _, work = create_completed_work(
        db,
        customer,
        worker_user,
    )

    response = client.post(
        "/reputations/",
        json={
            "work_id": work.id,
            "rating": 5,
            "comment": "I rate myself",
        },
        headers={
            "Authorization": f"Bearer {get_token(client, worker_user.email)}"
        },
    )

    assert response.status_code == 403


def test_reputation_requires_completed_work(client, db):
    customer = create_user(
        db,
        "Customer",
        "customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "worker@example.com",
    )

    worker = Worker(
        user_id=worker_user.id,
        is_available=False,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)

    job = Job(
        title="Repair",
        description="Repair something",
        location="Bhopal",
        budget=500,
        status="in_progress",
        customer_id=customer.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    assignment = Assignment(
        job_id=job.id,
        worker_id=worker.id,
        status="accepted",
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    work = Work(
        assignment_id=assignment.id,
        status="in_progress",
    )
    db.add(work)
    db.commit()
    db.refresh(work)

    response = client.post(
        "/reputations/",
        json={
            "work_id": work.id,
            "rating": 5,
        },
        headers={
            "Authorization": f"Bearer {get_token(client, customer.email)}"
        },
    )

    assert response.status_code == 403


def test_reputation_requires_confirmation(client, db):
    customer = create_user(
        db,
        "Customer",
        "customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "worker@example.com",
    )

    worker, job, assignment, work = create_completed_work(
        db,
        customer,
        worker_user,
    )

    db.query(Confirmation).filter(
        Confirmation.work_id == work.id
    ).delete()

    db.commit()

    response = client.post(
        "/reputations/",
        json={
            "work_id": work.id,
            "rating": 5,
        },
        headers={
            "Authorization": f"Bearer {get_token(client, customer.email)}"
        },
    )

    assert response.status_code == 403


def test_reputation_requires_paid_payment(client, db):
    customer = create_user(
        db,
        "Customer",
        "customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "worker@example.com",
    )

    worker, job, assignment, work = create_completed_work(
        db,
        customer,
        worker_user,
    )

    payment = (
        db.query(Payment)
        .filter(Payment.work_id == work.id)
        .first()
    )

    payment.status = "pending"
    db.commit()

    response = client.post(
        "/reputations/",
        json={
            "work_id": work.id,
            "rating": 5,
        },
        headers={
            "Authorization": f"Bearer {get_token(client, customer.email)}"
        },
    )

    assert response.status_code == 403


def test_duplicate_reputation_is_rejected(client, db):
    customer = create_user(
        db,
        "Customer",
        "customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "worker@example.com",
    )

    _, _, _, work = create_completed_work(
        db,
        customer,
        worker_user,
    )

    token = get_token(client, customer.email)

    first_response = client.post(
        "/reputations/",
        json={
            "work_id": work.id,
            "rating": 5,
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/reputations/",
        json={
            "work_id": work.id,
            "rating": 4,
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert second_response.status_code == 403


def test_customer_can_view_reputation(client, db):
    customer = create_user(
        db,
        "Customer",
        "customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "worker@example.com",
    )

    _, _, _, work = create_completed_work(
        db,
        customer,
        worker_user,
    )

    token = get_token(client, customer.email)

    create_response = client.post(
        "/reputations/",
        json={
            "work_id": work.id,
            "rating": 5,
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    reputation_id = create_response.json()["id"]

    response = client.get(
        f"/reputations/{reputation_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == reputation_id


def test_worker_can_view_received_reputation(client, db):
    customer = create_user(
        db,
        "Customer",
        "customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "worker@example.com",
    )

    _, _, _, work = create_completed_work(
        db,
        customer,
        worker_user,
    )

    customer_token = get_token(client, customer.email)

    create_response = client.post(
        "/reputations/",
        json={
            "work_id": work.id,
            "rating": 4,
            "comment": "Good work",
        },
        headers={
            "Authorization": f"Bearer {customer_token}"
        },
    )

    reputation_id = create_response.json()["id"]

    worker_token = get_token(client, worker_user.email)

    response = client.get(
        f"/reputations/{reputation_id}",
        headers={
            "Authorization": f"Bearer {worker_token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["rating"] == 4


def test_unrelated_user_cannot_view_reputation(client, db):
    customer = create_user(
        db,
        "Customer",
        "customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "worker@example.com",
    )

    unrelated_user = create_user(
        db,
        "Unrelated",
        "unrelated@example.com",
    )

    _, _, _, work = create_completed_work(
        db,
        customer,
        worker_user,
    )

    customer_token = get_token(client, customer.email)

    create_response = client.post(
        "/reputations/",
        json={
            "work_id": work.id,
            "rating": 5,
        },
        headers={
            "Authorization": f"Bearer {customer_token}"
        },
    )

    reputation_id = create_response.json()["id"]

    unrelated_token = get_token(
        client,
        unrelated_user.email,
    )

    response = client.get(
        f"/reputations/{reputation_id}",
        headers={
            "Authorization": f"Bearer {unrelated_token}"
        },
    )

    assert response.status_code == 403