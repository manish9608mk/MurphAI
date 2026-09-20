from backend.app.core.security import create_access_token
from backend.app.models.user import User


def auth_headers(user_id: int):
    token = create_access_token(user_id)

    return {
        "Authorization": f"Bearer {token}",
    }


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


def setup_work_flow(client, db):
    customer_id = create_user(
        db,
        "Customer",
        "work-flow-customer@example.com",
    )

    worker_user_id = create_user(
        db,
        "Rahul",
        "work-flow-worker@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    assignment_id = create_assignment(
        client,
        customer_id,
        job_id,
        worker_id,
    )

    accept_response = client.patch(
        f"/assignments/{assignment_id}/accept",
        headers=auth_headers(worker_user_id),
    )

    assert accept_response.status_code == 200

    return {
        "customer_id": customer_id,
        "worker_user_id": worker_user_id,
        "worker_id": worker_id,
        "job_id": job_id,
        "assignment_id": assignment_id,
    }


def test_worker_can_list_my_works(client, db):
    data = setup_work_flow(client, db)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_user_id"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/works/mine",
        headers=auth_headers(data["worker_user_id"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["assignment_id"] == data["assignment_id"]
    assert body[0]["job_title"] == "Fix leaking kitchen tap"
    assert body[0]["budget"] == 1500
    assert body[0]["status"] == "pending"


def test_customer_cannot_use_worker_work_list(client, db):
    customer_id = create_user(
        db,
        "Customer",
        "work-flow-customer-2@example.com",
    )

    response = client.get(
        "/works/mine",
        headers=auth_headers(customer_id),
    )

    assert response.status_code == 404


def test_worker_can_get_work_for_assignment(client, db):
    data = setup_work_flow(client, db)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_user_id"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/works/assignment/{data['assignment_id']}",
        headers=auth_headers(data["worker_user_id"]),
    )

    assert response.status_code == 200
    assert response.json()["assignment_id"] == data["assignment_id"]


def test_worker_start_work_updates_job(client, db):
    data = setup_work_flow(client, db)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_user_id"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    assert create_response.status_code == 201

    work_id = create_response.json()["id"]

    response = client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(data["worker_user_id"]),
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    assert response.json()["started_at"] is not None

    job_response = client.get(
        f"/jobs/{data['job_id']}",
        headers=auth_headers(data["customer_id"]),
    )

    assert job_response.status_code == 200
    assert job_response.json()["status"] == "in_progress"

def test_customer_can_get_work_for_job(client, db):
    """
    The customer who owns the Job can retrieve
    the Work connected to that Job.
    """

    data = setup_work_flow(client, db)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_user_id"]),
        json={
            "assignment_id": data["assignment_id"],
            "description": "Kitchen tap repair completed",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/works/job/{data['job_id']}",
        headers=auth_headers(data["customer_id"]),
    )

    assert response.status_code == 200
    assert response.json()["assignment_id"] == data["assignment_id"]


def test_worker_can_get_work_for_job(client, db):
    """
    The assigned worker can retrieve the Work
    connected to the Job.
    """

    data = setup_work_flow(client, db)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_user_id"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/works/job/{data['job_id']}",
        headers=auth_headers(data["worker_user_id"]),
    )

    assert response.status_code == 200
    assert response.json()["id"] == create_response.json()["id"]


def test_unrelated_user_cannot_get_work_for_job(client, db):
    """
    An unrelated user cannot retrieve Work
    connected to another user's Job.
    """

    data = setup_work_flow(client, db)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_user_id"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    assert create_response.status_code == 201

    other_user_id = create_user(
        db,
        "Other User",
        "work-job-unrelated@example.com",
    )

    response = client.get(
        f"/works/job/{data['job_id']}",
        headers=auth_headers(other_user_id),
    )

    assert response.status_code == 403


def test_get_work_for_job_requires_existing_work(client, db):
    """
    A Job without a Work record cannot return Work.
    """

    data = setup_work_flow(client, db)

    response = client.get(
        f"/works/job/{data['job_id']}",
        headers=auth_headers(data["customer_id"]),
    )

    assert response.status_code == 403