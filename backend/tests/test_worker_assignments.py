from backend.app.core.security import create_access_token
from backend.app.models.user import User


def auth_headers(user_id: int):
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def create_user(db, name, email):
    user = User(
        name=name,
        email=email,
        password_hash="test-password-hash",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id


def create_worker(client, user_id):
    response = client.post(
        "/workers/",
        headers=auth_headers(user_id),
        json={
            "bio": "Reliable worker",
            "location": "Bhopal",
            "experience_years": 3,
            "is_available": True,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_job(client, customer_id):
    response = client.post(
        "/jobs/",
        headers=auth_headers(customer_id),
        json={
            "title": "Fix leaking kitchen tap",
            "description": "Repair the kitchen tap and stop the water leak.",
            "location": "Bhopal",
            "budget": 1500,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_assignment(client, customer_id, job_id, worker_id):
    response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_worker_can_list_my_assignments(client, db):
    customer_id = create_user(
        db,
        "Customer",
        "worker-assignment-customer@example.com",
    )
    worker_user_id = create_user(
        db,
        "Rahul",
        "worker-assignment-worker@example.com",
    )
    worker_id = create_worker(client, worker_user_id)
    job_id = create_job(client, customer_id)
    create_assignment(client, customer_id, job_id, worker_id)

    response = client.get(
        "/assignments/mine",
        headers=auth_headers(worker_user_id),
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["status"] == "pending"
    assert data[0]["job_id"] == job_id
    assert data[0]["worker_id"] == worker_id
    assert data[0]["job_title"] == "Fix leaking kitchen tap"
    assert data[0]["location"] == "Bhopal"
    assert data[0]["budget"] == 1500
    assert data[0]["job_status"] == "open"


def test_customer_cannot_use_worker_assignment_list(client, db):
    customer_id = create_user(
        db,
        "Customer",
        "worker-assignment-customer-2@example.com",
    )

    response = client.get(
        "/assignments/mine",
        headers=auth_headers(customer_id),
    )

    assert response.status_code == 404


def test_worker_can_accept_assignment_from_real_flow(client, db):
    customer_id = create_user(
        db,
        "Customer",
        "worker-assignment-customer-3@example.com",
    )
    worker_user_id = create_user(
        db,
        "Rahul",
        "worker-assignment-worker-3@example.com",
    )
    worker_id = create_worker(client, worker_user_id)
    job_id = create_job(client, customer_id)
    assignment_id = create_assignment(
        client,
        customer_id,
        job_id,
        worker_id,
    )

    response = client.patch(
        f"/assignments/{assignment_id}/accept",
        headers=auth_headers(worker_user_id),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

    job_response = client.get(
        f"/jobs/{job_id}",
        headers=auth_headers(worker_user_id),
    )

    assert job_response.status_code == 200
    assert job_response.json()["status"] == "assigned"


def test_worker_cannot_accept_second_assignment_after_becoming_unavailable(
    client,
    db,
):
    customer_one = create_user(
        db,
        "Customer One",
        "worker-assignment-concurrency-customer-1@example.com",
    )
    customer_two = create_user(
        db,
        "Customer Two",
        "worker-assignment-concurrency-customer-2@example.com",
    )
    worker_user_id = create_user(
        db,
        "Rahul",
        "worker-assignment-concurrency-worker@example.com",
    )

    worker_id = create_worker(client, worker_user_id)
    first_job_id = create_job(client, customer_one)
    second_job_id = create_job(client, customer_two)

    first_assignment_id = create_assignment(
        client,
        customer_one,
        first_job_id,
        worker_id,
    )
    second_assignment_id = create_assignment(
        client,
        customer_two,
        second_job_id,
        worker_id,
    )

    first_response = client.patch(
        f"/assignments/{first_assignment_id}/accept",
        headers=auth_headers(worker_user_id),
    )

    second_response = client.patch(
        f"/assignments/{second_assignment_id}/accept",
        headers=auth_headers(worker_user_id),
    )

    assert first_response.status_code == 200
    assert first_response.json()["status"] == "accepted"
    assert second_response.status_code == 400
