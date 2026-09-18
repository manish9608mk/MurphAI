from backend.app.core.security import create_access_token
from backend.app.models.user import User


def create_test_user(
    db,
    name: str,
    email: str,
):
    user = User(
        name=name,
        email=email,
        password_hash="test-password-hash",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user.id


def auth_headers(user_id: int):
    token = create_access_token(user_id)

    return {
        "Authorization": f"Bearer {token}",
    }


def create_worker(
    client,
    user_id: int,
):
    response = client.post(
        "/workers/",
        headers=auth_headers(user_id),
        json={
            "bio": "Experienced electrician",
            "location": "Bhopal",
            "experience_years": 5,
            "is_available": True,
        },
    )

    assert response.status_code == 201


def create_job(
    client,
    customer_id: int,
    title: str,
    status: str = "open",
):
    response = client.post(
        "/jobs/",
        headers=auth_headers(customer_id),
        json={
            "title": title,
            "description": (
                "Need professional help "
                "to complete this job."
            ),
            "location": "Bhopal",
            "budget": 2500,
        },
    )

    assert response.status_code == 201

    job_id = response.json()["id"]

    if status != "open":
        status_response = client.patch(
            f"/jobs/{job_id}/status",
            headers=auth_headers(customer_id),
            json={
                "status": status,
            },
        )

        assert status_response.status_code == 200

    return job_id


def test_worker_can_discover_open_jobs(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer One",
        "customer1@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker One",
        "worker1@example.com",
    )

    create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
        "Fix Kitchen Sink",
    )

    response = client.get(
        "/jobs/available",
        headers=auth_headers(worker_user_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == job_id
    assert data[0]["title"] == "Fix Kitchen Sink"
    assert data[0]["status"] == "open"


def test_worker_cannot_discover_own_job(
    client,
    db,
):
    user_id = create_test_user(
        db,
        "Customer Worker",
        "sameuser@example.com",
    )

    create_worker(
        client,
        user_id,
    )

    create_job(
        client,
        user_id,
        "My Own Job",
    )

    response = client.get(
        "/jobs/available",
        headers=auth_headers(user_id),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_closed_jobs_are_not_discoverable(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Two",
        "customer2@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Two",
        "worker2@example.com",
    )

    create_worker(
        client,
        worker_user_id,
    )

    create_job(
        client,
        customer_id,
        "Closed Job",
        status="cancelled",
    )

    response = client.get(
        "/jobs/available",
        headers=auth_headers(worker_user_id),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_only_open_jobs_are_returned(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Three",
        "customer3@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Three",
        "worker3@example.com",
    )

    create_worker(
        client,
        worker_user_id,
    )

    open_job_id = create_job(
        client,
        customer_id,
        "Open Job",
    )

    create_job(
        client,
        customer_id,
        "Cancelled Job",
        status="cancelled",
    )

    response = client.get(
        "/jobs/available",
        headers=auth_headers(worker_user_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == open_job_id


def test_multiple_open_jobs_are_returned(
    client,
    db,
):
    customer_one_id = create_test_user(
        db,
        "Customer Four",
        "customer4@example.com",
    )

    customer_two_id = create_test_user(
        db,
        "Customer Five",
        "customer5@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Four",
        "worker4@example.com",
    )

    create_worker(
        client,
        worker_user_id,
    )

    first_job_id = create_job(
        client,
        customer_one_id,
        "Repair Fan",
    )

    second_job_id = create_job(
        client,
        customer_two_id,
        "Install Light",
    )

    response = client.get(
        "/jobs/available",
        headers=auth_headers(worker_user_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    returned_ids = {
        item["id"]
        for item in data
    }

    assert returned_ids == {
        first_job_id,
        second_job_id,
    }


def test_available_jobs_require_authentication(
    client,
):
    response = client.get(
        "/jobs/available",
    )

    assert response.status_code == 401