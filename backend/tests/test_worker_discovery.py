from backend.app.core.security import (
    create_access_token,
    hash_password,
)
from backend.app.models.assignment import Assignment
from backend.app.models.confirmation import Confirmation
from backend.app.models.payment import Payment
from backend.app.models.reputation import Reputation
from backend.app.models.skill import Skill, worker_skills
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
    bio,
    location,
    experience_years,
    is_available,
):
    worker = Worker(
        user_id=user.id,
        bio=bio,
        location=location,
        experience_years=experience_years,
        is_available=is_available,
    )

    db.add(worker)
    db.commit()
    db.refresh(worker)

    return worker


def create_skill(db, name):
    skill = Skill(
        name=name,
        normalized_name=name.lower(),
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    return skill


def attach_skill(db, worker, skill):
    db.execute(
        worker_skills.insert().values(
            worker_id=worker.id,
            skill_id=skill.id,
        )
    )
    db.commit()


def create_verified_work(
    db,
    customer,
    worker,
):
    from backend.app.models.job import Job

    job = Job(
        title="Wiring repair",
        description="Electrical repair",
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
        description="Electrical wiring repaired",
    )

    db.add(work)
    db.commit()
    db.refresh(work)

    confirmation = Confirmation(
        work_id=work.id,
        customer_id=customer.id,
        comment="Confirmed",
    )

    payment = Payment(
        work_id=work.id,
        customer_id=customer.id,
        worker_id=worker.id,
        amount=1500,
        status="paid",
        transaction_reference="PRIVATE-DISCOVERY-TXN",
    )

    reputation = Reputation(
        work_id=work.id,
        customer_id=customer.id,
        worker_id=worker.id,
        rating=5,
        comment="Excellent work",
    )

    db.add_all([
        confirmation,
        payment,
        reputation,
    ])

    db.commit()


def test_worker_discovery_requires_authentication(
    client,
):
    response = client.get(
        "/workers/discover",
    )

    assert response.status_code == 401


def test_worker_discovery_returns_public_workers(
    client,
    db,
):
    viewer = create_user(
        db,
        "Customer",
        "discovery-viewer@example.com",
    )

    worker_user = create_user(
        db,
        "Rahul",
        "rahul-discovery@example.com",
    )

    worker = create_worker(
        db,
        worker_user,
        "Reliable electrician",
        "Bhopal",
        5,
        True,
    )

    response = client.get(
        "/workers/discover",
        headers=auth_headers(viewer.id),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["workers"][0]["worker_id"] == worker.id
    assert data["workers"][0]["name"] == "Rahul"
    assert data["workers"][0]["location"] == "Bhopal"
    assert "email" not in data["workers"][0]
    assert "user_id" not in data["workers"][0]


def test_worker_discovery_includes_verified_summary(
    client,
    db,
):
    viewer = create_user(
        db,
        "Customer",
        "discovery-summary-viewer@example.com",
    )

    worker_user = create_user(
        db,
        "Verified Worker",
        "verified-discovery@example.com",
    )

    worker = create_worker(
        db,
        worker_user,
        "Experienced electrician",
        "Bhopal",
        7,
        True,
    )

    create_verified_work(
        db,
        viewer,
        worker,
    )

    response = client.get(
        "/workers/discover",
        headers=auth_headers(viewer.id),
    )

    data = response.json()

    worker_data = data["workers"][0]

    assert worker_data["verified_work_count"] == 1
    assert worker_data["average_rating"] == 5.0


def test_worker_discovery_available_only(
    client,
    db,
):
    viewer = create_user(
        db,
        "Customer",
        "availability-viewer@example.com",
    )

    available_user = create_user(
        db,
        "Available Worker",
        "available@example.com",
    )

    unavailable_user = create_user(
        db,
        "Unavailable Worker",
        "unavailable@example.com",
    )

    create_worker(
        db,
        available_user,
        "Available",
        "Bhopal",
        3,
        True,
    )

    create_worker(
        db,
        unavailable_user,
        "Unavailable",
        "Bhopal",
        4,
        False,
    )

    response = client.get(
        "/workers/discover?available_only=true",
        headers=auth_headers(viewer.id),
    )

    data = response.json()

    assert data["total"] == 1
    assert data["workers"][0]["name"] == "Available Worker"


def test_worker_discovery_search(
    client,
    db,
):
    viewer = create_user(
        db,
        "Customer",
        "search-viewer@example.com",
    )

    electrician_user = create_user(
        db,
        "Rahul",
        "search-rahul@example.com",
    )

    plumber_user = create_user(
        db,
        "Amit",
        "search-amit@example.com",
    )

    create_worker(
        db,
        electrician_user,
        "Professional electrician",
        "Bhopal",
        5,
        True,
    )

    create_worker(
        db,
        plumber_user,
        "Professional plumber",
        "Indore",
        6,
        True,
    )

    response = client.get(
        "/workers/discover?search=electrician",
        headers=auth_headers(viewer.id),
    )

    data = response.json()

    assert data["total"] == 1
    assert data["workers"][0]["name"] == "Rahul"


def test_worker_discovery_skill_filter(
    client,
    db,
):
    viewer = create_user(
        db,
        "Customer",
        "skill-viewer@example.com",
    )

    worker_user = create_user(
        db,
        "Skilled Worker",
        "skilled-discovery@example.com",
    )

    worker = create_worker(
        db,
        worker_user,
        "Electrical specialist",
        "Bhopal",
        8,
        True,
    )

    skill = create_skill(
        db,
        "Electrical Wiring",
    )

    attach_skill(
        db,
        worker,
        skill,
    )

    response = client.get(
        "/workers/discover?skill=wiring",
        headers=auth_headers(viewer.id),
    )

    data = response.json()

    assert data["total"] == 1
    assert data["workers"][0]["skills"] == [
        "Electrical Wiring",
    ]


def test_worker_discovery_location_filter(
    client,
    db,
):
    viewer = create_user(
        db,
        "Customer",
        "location-viewer@example.com",
    )

    bhopal_user = create_user(
        db,
        "Bhopal Worker",
        "bhopal-discovery@example.com",
    )

    indore_user = create_user(
        db,
        "Indore Worker",
        "indore-discovery@example.com",
    )

    create_worker(
        db,
        bhopal_user,
        "Worker in Bhopal",
        "Bhopal",
        3,
        True,
    )

    create_worker(
        db,
        indore_user,
        "Worker in Indore",
        "Indore",
        4,
        True,
    )

    response = client.get(
        "/workers/discover?location=bhopal",
        headers=auth_headers(viewer.id),
    )

    data = response.json()

    assert data["total"] == 1
    assert data["workers"][0]["name"] == "Bhopal Worker"


def test_worker_discovery_pagination(
    client,
    db,
):
    viewer = create_user(
        db,
        "Customer",
        "pagination-viewer@example.com",
    )

    for index in range(3):
        worker_user = create_user(
            db,
            f"Worker {index}",
            f"pagination-{index}@example.com",
        )

        create_worker(
            db,
            worker_user,
            "Worker",
            "Bhopal",
            index + 1,
            True,
        )

    response = client.get(
        "/workers/discover?limit=2&offset=1",
        headers=auth_headers(viewer.id),
    )

    data = response.json()

    assert data["total"] == 3
    assert len(data["workers"]) == 2


def test_worker_discovery_excludes_private_payment_data(
    client,
    db,
):
    viewer = create_user(
        db,
        "Customer",
        "privacy-viewer@example.com",
    )

    worker_user = create_user(
        db,
        "Private Worker",
        "private-worker@example.com",
    )

    worker = create_worker(
        db,
        worker_user,
        "Private-test worker",
        "Bhopal",
        4,
        True,
    )

    create_verified_work(
        db,
        viewer,
        worker,
    )

    response = client.get(
        "/workers/discover",
        headers=auth_headers(viewer.id),
    )

    worker_data = response.json()["workers"][0]

    assert "email" not in worker_data
    assert "user_id" not in worker_data
    assert "payment_id" not in worker_data
    assert "amount" not in worker_data
    assert "transaction_reference" not in worker_data
