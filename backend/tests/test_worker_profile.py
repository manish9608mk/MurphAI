from backend.app.core.security import create_access_token, hash_password
from backend.app.models.assignment import Assignment
from backend.app.models.confirmation import Confirmation
from backend.app.models.job import Job
from backend.app.models.payment import Payment
from backend.app.models.reputation import Reputation
from backend.app.models.user import User
from backend.app.models.worker import Worker
from backend.app.models.work import Work


def create_user(
    db,
    name,
    email,
):
    user = User(
        name=name,
        email=email,
        password_hash=hash_password("password"),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def auth_headers(user_id):
    token = create_access_token(user_id)

    return {
        "Authorization": f"Bearer {token}",
    }


def create_worker(
    db,
    user,
):
    worker = Worker(
        user_id=user.id,
        bio="Reliable local electrician",
        location="Bhopal",
        experience_years=5,
        is_available=True,
    )

    db.add(worker)
    db.commit()
    db.refresh(worker)

    return worker


def create_verified_work(
    db,
    customer,
    worker,
    title="Kitchen Tap Repair",
    rating=4,
):
    job = Job(
        title=title,
        description="Repair leaking kitchen tap",
        location="Bhopal",
        budget=1500,
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
        description="Repaired the leaking tap joint",
    )

    db.add(work)
    db.commit()
    db.refresh(work)

    confirmation = Confirmation(
        work_id=work.id,
        customer_id=customer.id,
        comment="Work completed successfully",
    )

    payment = Payment(
        work_id=work.id,
        customer_id=customer.id,
        worker_id=worker.id,
        amount=1500,
        status="paid",
        transaction_reference="PRIVATE-TXN-001",
    )

    reputation = Reputation(
        work_id=work.id,
        customer_id=customer.id,
        worker_id=worker.id,
        rating=rating,
        comment="extremely satisfied",
    )

    db.add_all([
        confirmation,
        payment,
        reputation,
    ])

    db.commit()

    return work


def test_public_worker_profile_requires_authentication(
    client,
    db,
):
    user = create_user(
        db,
        "Worker",
        "worker-profile-auth@example.com",
    )

    worker = create_worker(
        db,
        user,
    )

    response = client.get(
        f"/workers/{worker.id}/profile",
    )

    assert response.status_code == 401


def test_public_worker_profile_returns_worker_details(
    client,
    db,
):
    user = create_user(
        db,
        "Rahul",
        "rahul-profile@example.com",
    )

    worker = create_worker(
        db,
        user,
    )

    response = client.get(
        f"/workers/{worker.id}/profile",
        headers=auth_headers(user.id),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["worker_id"] == worker.id
    assert data["name"] == "Rahul"
    assert data["bio"] == "Reliable local electrician"
    assert data["location"] == "Bhopal"
    assert data["experience_years"] == 5
    assert data["is_available"] is True


def test_other_authenticated_user_can_view_profile(
    client,
    db,
):
    worker_user = create_user(
        db,
        "Worker",
        "worker-public@example.com",
    )

    viewer = create_user(
        db,
        "Customer",
        "customer-viewer@example.com",
    )

    worker = create_worker(
        db,
        worker_user,
    )

    response = client.get(
        f"/workers/{worker.id}/profile",
        headers=auth_headers(viewer.id),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Worker"


def test_public_worker_profile_includes_skills(
    client,
    db,
):
    user = create_user(
        db,
        "Skilled Worker",
        "skilled-worker@example.com",
    )

    worker = create_worker(
        db,
        user,
    )

    first_skill = client.post(
        f"/workers/{worker.id}/skills",
        headers=auth_headers(user.id),
        json={
            "name": "Electrician",
        },
    )

    second_skill = client.post(
        f"/workers/{worker.id}/skills",
        headers=auth_headers(user.id),
        json={
            "name": "Wiring",
        },
    )

    assert first_skill.status_code == 201
    assert second_skill.status_code == 201

    response = client.get(
        f"/workers/{worker.id}/profile",
        headers=auth_headers(user.id),
    )

    assert response.status_code == 200

    assert response.json()["skills"] == [
        "Electrician",
        "Wiring",
    ]


def test_public_worker_profile_includes_verified_work_summary(
    client,
    db,
):
    customer = create_user(
        db,
        "Customer",
        "profile-customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "profile-worker@example.com",
    )

    worker = create_worker(
        db,
        worker_user,
    )

    create_verified_work(
        db,
        customer,
        worker,
    )

    response = client.get(
        f"/workers/{worker.id}/profile",
        headers=auth_headers(customer.id),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["verified_work_count"] == 1
    assert data["average_rating"] == 4.0

    assert len(data["reviews"]) == 1

    review = data["reviews"][0]

    assert review["job_title"] == "Kitchen Tap Repair"
    assert review["rating"] == 4
    assert review["comment"] == "extremely satisfied"


def test_public_worker_profile_excludes_unverified_work(
    client,
    db,
):
    customer = create_user(
        db,
        "Customer",
        "profile-unverified-customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "profile-unverified-worker@example.com",
    )

    worker = create_worker(
        db,
        worker_user,
    )

    verified_work = create_verified_work(
        db,
        customer,
        worker,
        title="Verified Repair",
    )

    unverified_job = Job(
        title="Pending Payment Repair",
        description="Repair something",
        location="Bhopal",
        budget=2000,
        status="completed",
        customer_id=customer.id,
    )

    db.add(unverified_job)
    db.commit()
    db.refresh(unverified_job)

    assignment = Assignment(
        job_id=unverified_job.id,
        worker_id=worker.id,
        status="accepted",
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    unverified_work = Work(
        assignment_id=assignment.id,
        status="completed",
        description="Repair completed",
    )

    db.add(unverified_work)
    db.commit()
    db.refresh(unverified_work)

    confirmation = Confirmation(
        work_id=unverified_work.id,
        customer_id=customer.id,
        comment="Confirmed",
    )

    pending_payment = Payment(
        work_id=unverified_work.id,
        customer_id=customer.id,
        worker_id=worker.id,
        amount=2000,
        status="pending",
    )

    db.add_all([
        confirmation,
        pending_payment,
    ])

    db.commit()

    response = client.get(
        f"/workers/{worker.id}/profile",
        headers=auth_headers(customer.id),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["verified_work_count"] == 1
    assert data["reviews"][0]["work_id"] == verified_work.id


def test_public_worker_profile_does_not_expose_private_payment_data(
    client,
    db,
):
    customer = create_user(
        db,
        "Customer",
        "profile-private-customer@example.com",
    )

    worker_user = create_user(
        db,
        "Worker",
        "profile-private-worker@example.com",
    )

    worker = create_worker(
        db,
        worker_user,
    )

    create_verified_work(
        db,
        customer,
        worker,
    )

    response = client.get(
        f"/workers/{worker.id}/profile",
        headers=auth_headers(customer.id),
    )

    assert response.status_code == 200

    data = response.json()

    assert "email" not in data
    assert "customer_id" not in data
    assert "payment" not in data
    assert "payment_id" not in data
    assert "amount" not in data
    assert "transaction_reference" not in data

    review = data["reviews"][0]

    assert "customer_id" not in review
    assert "payment" not in review
    assert "amount" not in review


def test_public_worker_profile_returns_404_for_unknown_worker(
    client,
    db,
):
    viewer = create_user(
        db,
        "Viewer",
        "profile-unknown@example.com",
    )

    response = client.get(
        "/workers/999999/profile",
        headers=auth_headers(viewer.id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Worker not found"
