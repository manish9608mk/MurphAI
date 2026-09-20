from backend.app.core.security import hash_password
from backend.app.models.assignment import Assignment
from backend.app.models.confirmation import Confirmation
from backend.app.models.evidence import Evidence
from backend.app.models.job import Job
from backend.app.models.payment import Payment
from backend.app.models.reputation import Reputation
from backend.app.models.user import User
from backend.app.models.worker import Worker
from backend.app.models.work import Work


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


def get_token(client, email):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "password",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
    }


def create_worker(db, user):
    worker = Worker(
        user_id=user.id,
        bio="Experienced electrician",
        location="Bhopal",
        experience_years=5,
        is_available=False,
    )

    db.add(worker)
    db.commit()
    db.refresh(worker)

    return worker


def create_work_record(
    db,
    customer,
    worker,
    title="Electrical Repair",
    budget=1500,
    confirmed=True,
    payment_status="paid",
    rating=None,
):
    job = Job(
        title=title,
        description="Repair electrical wiring",
        location="Bhopal",
        budget=budget,
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

    evidence = Evidence(
        work_id=work.id,
        evidence_type="photo",
        description="Final repair photo",
        url="https://example.com/final-photo.jpg",
    )

    db.add(evidence)

    if confirmed:
        confirmation = Confirmation(
            work_id=work.id,
            customer_id=customer.id,
            comment="Work completed successfully",
        )

        db.add(confirmation)

    payment = Payment(
        work_id=work.id,
        customer_id=customer.id,
        worker_id=worker.id,
        amount=budget,
        status=payment_status,
        transaction_reference="TEST-TXN-001",
    )

    db.add(payment)

    if rating is not None:
        reputation = Reputation(
            work_id=work.id,
            customer_id=customer.id,
            worker_id=worker.id,
            rating=rating,
            comment="Excellent work",
        )

        db.add(reputation)

    db.commit()

    return work


def test_worker_history_requires_authentication(client):
    response = client.get("/workers/me/history")

    assert response.status_code == 401


def test_worker_history_requires_worker_profile(client, db):
    user = create_user(
        db,
        "User Without Worker",
        "no-worker@example.com",
    )

    token = get_token(
        client,
        user.email,
    )

    response = client.get(
        "/workers/me/history",
        headers=auth_headers(token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Worker not found"


def test_worker_history_returns_empty_for_new_worker(client, db):
    user = create_user(
        db,
        "New Worker",
        "new-worker@example.com",
    )

    create_worker(
        db,
        user,
    )

    token = get_token(
        client,
        user.email,
    )

    response = client.get(
        "/workers/me/history",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["worker_id"] > 0
    assert data["total_verified_works"] == 0
    assert data["average_rating"] is None
    assert data["works"] == []


def test_worker_history_contains_only_verified_work(
    client,
    db,
):
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

    worker = create_worker(
        db,
        worker_user,
    )

    # Verified: completed + confirmed + paid.
    verified_work = create_work_record(
        db,
        customer,
        worker,
        title="Verified Electrical Repair",
        payment_status="paid",
        confirmed=True,
        rating=5,
    )

    # Not verified: payment is still pending.
    pending_payment_work = create_work_record(
        db,
        customer,
        worker,
        title="Pending Payment Repair",
        payment_status="pending",
        confirmed=True,
    )

    # Not verified: customer has not confirmed.
    unconfirmed_work = create_work_record(
        db,
        customer,
        worker,
        title="Unconfirmed Repair",
        payment_status="paid",
        confirmed=False,
    )

    token = get_token(
        client,
        worker_user.email,
    )

    response = client.get(
        "/workers/me/history",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_verified_works"] == 1
    assert data["works"][0]["work_id"] == verified_work.id

    returned_work_ids = {
        item["work_id"]
        for item in data["works"]
    }

    assert pending_payment_work.id not in returned_work_ids
    assert unconfirmed_work.id not in returned_work_ids


def test_worker_history_includes_evidence_confirmation_payment_and_reputation(
    client,
    db,
):
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

    worker = create_worker(
        db,
        worker_user,
    )

    work = create_work_record(
        db,
        customer,
        worker,
        title="Kitchen Tap Repair",
        budget=1500,
        confirmed=True,
        payment_status="paid",
        rating=4,
    )

    token = get_token(
        client,
        worker_user.email,
    )

    response = client.get(
        "/workers/me/history",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    item = response.json()["works"][0]

    assert item["work_id"] == work.id
    assert item["job_title"] == "Kitchen Tap Repair"
    assert item["budget"] == 1500
    assert item["work_description"] == "Electrical wiring repaired"

    assert len(item["evidence"]) == 1
    assert item["evidence"][0]["evidence_type"] == "photo"
    assert item["evidence"][0]["url"] == (
        "https://example.com/final-photo.jpg"
    )

    assert item["confirmation"]["work_id"] == work.id
    assert item["confirmation"]["comment"] == (
        "Work completed successfully"
    )

    assert item["payment"]["work_id"] == work.id
    assert item["payment"]["status"] == "paid"
    assert item["payment"]["amount"] == 1500

    assert item["reputation"]["work_id"] == work.id
    assert item["reputation"]["rating"] == 4
    assert item["reputation"]["comment"] == "Excellent work"

    assert response.json()["average_rating"] == 4.0


def test_worker_history_only_returns_the_authenticated_workers_work(
    client,
    db,
):
    customer = create_user(
        db,
        "Customer",
        "customer@example.com",
    )

    worker_one_user = create_user(
        db,
        "Worker One",
        "worker-one@example.com",
    )

    worker_two_user = create_user(
        db,
        "Worker Two",
        "worker-two@example.com",
    )

    worker_one = create_worker(
        db,
        worker_one_user,
    )

    worker_two = create_worker(
        db,
        worker_two_user,
    )

    worker_one_work = create_work_record(
        db,
        customer,
        worker_one,
        title="Worker One Repair",
    )

    worker_two_work = create_work_record(
        db,
        customer,
        worker_two,
        title="Worker Two Repair",
    )

    token = get_token(
        client,
        worker_one_user.email,
    )

    response = client.get(
        "/workers/me/history",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    returned_work_ids = {
        item["work_id"]
        for item in data["works"]
    }

    assert worker_one_work.id in returned_work_ids
    assert worker_two_work.id not in returned_work_ids
