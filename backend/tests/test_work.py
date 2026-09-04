import pytest


# ============================================================
# Helper Functions
# ============================================================

def create_user(client, name, email, password="password123"):
    """
    Create a user and return the response.
    """

    return client.post(
        "/users/",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )


def login_user(client, email, password="password123"):
    """
    Login a user and return the access token.
    """

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_headers(token):
    """
    Create Authorization headers.
    """

    return {
        "Authorization": f"Bearer {token}",
    }


def create_worker(client, token):
    """
    Create a worker profile.
    """

    return client.post(
        "/workers/",
        headers=auth_headers(token),
        json={
            "bio": "Experienced electrician",
            "location": "Bhopal",
            "experience_years": 5,
            "is_available": True,
        },
    )


def create_job(client, token):
    """
    Create an OPEN job.
    """

    return client.post(
        "/jobs/",
        headers=auth_headers(token),
        json={
            "title": "Electrical Repair",
            "description": "Repair electrical wiring",
            "location": "Bhopal",
            "budget": 5000,
        },
    )


def create_assignment(client, token, job_id, worker_id):
    """
    Create an assignment for a worker.
    """

    return client.post(
        "/assignments/",
        headers=auth_headers(token),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )


def accept_assignment(client, token, assignment_id):
    """
    Worker accepts an assignment.
    """

    return client.patch(
        f"/assignments/{assignment_id}/accept",
        headers=auth_headers(token),
    )


def setup_work(client):
    """
    Create:

        Customer
        Worker
        Job
        Assignment
        Accepted Assignment

    Returns everything required to test Work.
    """

    # --------------------------------------------------------
    # Customer
    # --------------------------------------------------------

    create_user(
        client,
        "Customer",
        "customer@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    # --------------------------------------------------------
    # Worker
    # --------------------------------------------------------

    create_user(
        client,
        "Worker",
        "worker@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    worker_response = create_worker(
        client,
        worker_token,
    )

    assert worker_response.status_code == 201

    worker_id = worker_response.json()["id"]

    # --------------------------------------------------------
    # Job
    # --------------------------------------------------------

    job_response = create_job(
        client,
        customer_token,
    )

    assert job_response.status_code == 201

    job_id = job_response.json()["id"]

    # --------------------------------------------------------
    # Assignment
    # --------------------------------------------------------

    assignment_response = create_assignment(
        client,
        customer_token,
        job_id,
        worker_id,
    )

    assert assignment_response.status_code == 201

    assignment_id = assignment_response.json()["id"]

    # --------------------------------------------------------
    # Worker accepts assignment
    # --------------------------------------------------------

    accept_response = accept_assignment(
        client,
        worker_token,
        assignment_id,
    )

    assert accept_response.status_code == 200

    return {
        "customer_token": customer_token,
        "worker_token": worker_token,
        "worker_id": worker_id,
        "job_id": job_id,
        "assignment_id": assignment_id,
    }


# ============================================================
# Create Work Tests
# ============================================================

def test_create_work(client):
    """
    Assigned worker can create Work.
    """

    data = setup_work(client)

    response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
            "description": "Started electrical repair",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["assignment_id"] == data["assignment_id"]
    assert body["status"] == "pending"
    assert body["description"] == "Started electrical repair"


def test_non_assigned_user_cannot_create_work(client):
    """
    A different user cannot create Work
    for another worker's assignment.
    """

    data = setup_work(client)

    create_user(
        client,
        "Other User",
        "other@example.com",
    )

    other_token = login_user(
        client,
        "other@example.com",
    )

    response = client.post(
        "/works/",
        headers=auth_headers(other_token),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    assert response.status_code == 403


def test_work_requires_accepted_assignment(client):
    """
    Work cannot be created before the assignment
    has been accepted.
    """

    create_user(
        client,
        "Customer",
        "customer@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    create_user(
        client,
        "Worker",
        "worker@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    worker_response = create_worker(
        client,
        worker_token,
    )

    worker_id = worker_response.json()["id"]

    job_response = create_job(
        client,
        customer_token,
    )

    job_id = job_response.json()["id"]

    assignment_response = create_assignment(
        client,
        customer_token,
        job_id,
        worker_id,
    )

    assignment_id = assignment_response.json()["id"]

    # Assignment is still pending.

    response = client.post(
        "/works/",
        headers=auth_headers(worker_token),
        json={
            "assignment_id": assignment_id,
        },
    )

    assert response.status_code == 403


def test_duplicate_work_not_allowed(client):
    """
    One assignment can have only one Work record.
    """

    data = setup_work(client)

    first_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    assert second_response.status_code == 403


# ============================================================
# Get Work Tests
# ============================================================

def test_worker_can_view_work(client):
    """
    Assigned worker can view Work.
    """

    data = setup_work(client)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    work_id = create_response.json()["id"]

    response = client.get(
        f"/works/{work_id}",
        headers=auth_headers(data["worker_token"]),
    )

    assert response.status_code == 200
    assert response.json()["id"] == work_id


def test_customer_can_view_work(client):
    """
    Customer who created the Job can view Work.
    """

    data = setup_work(client)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    work_id = create_response.json()["id"]

    response = client.get(
        f"/works/{work_id}",
        headers=auth_headers(data["customer_token"]),
    )

    assert response.status_code == 200


def test_unrelated_user_cannot_view_work(client):
    """
    An unrelated user cannot view Work.
    """

    data = setup_work(client)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    work_id = create_response.json()["id"]

    create_user(
        client,
        "Other User",
        "other@example.com",
    )

    other_token = login_user(
        client,
        "other@example.com",
    )

    response = client.get(
        f"/works/{work_id}",
        headers=auth_headers(other_token),
    )

    assert response.status_code == 403


# ============================================================
# Update Work Tests
# ============================================================

def test_worker_can_update_work(client):
    """
    Assigned worker can update Work description.
    """

    data = setup_work(client)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
            "description": "Initial description",
        },
    )

    work_id = create_response.json()["id"]

    response = client.put(
        f"/works/{work_id}",
        headers=auth_headers(data["worker_token"]),
        json={
            "description": "Updated description",
        },
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"


def test_customer_cannot_update_work(client):
    """
    Customer cannot modify Work.
    """

    data = setup_work(client)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    work_id = create_response.json()["id"]

    response = client.put(
        f"/works/{work_id}",
        headers=auth_headers(data["customer_token"]),
        json={
            "description": "Customer changed this",
        },
    )

    assert response.status_code == 403


# ============================================================
# Work Status Tests
# ============================================================

def test_work_status_pending_to_in_progress(client):
    """
    Work can move from pending to in_progress.
    """

    data = setup_work(client)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    work_id = create_response.json()["id"]

    response = client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(data["worker_token"]),
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    assert response.json()["started_at"] is not None


def test_work_status_in_progress_to_completed(client):
    """
    Work can move from in_progress to completed.
    """

    data = setup_work(client)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    work_id = create_response.json()["id"]

    client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(data["worker_token"]),
        json={
            "status": "in_progress",
        },
    )

    response = client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(data["worker_token"]),
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["completed_at"] is not None


def test_work_cannot_skip_status(client):
    """
    Work cannot move directly from pending to completed.
    """

    data = setup_work(client)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    work_id = create_response.json()["id"]

    response = client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(data["worker_token"]),
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 403


def test_completed_work_cannot_change_status(client):
    """
    Completed Work cannot move to another status.
    """

    data = setup_work(client)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    work_id = create_response.json()["id"]

    client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(data["worker_token"]),
        json={
            "status": "in_progress",
        },
    )

    client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(data["worker_token"]),
        json={
            "status": "completed",
        },
    )

    response = client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(data["worker_token"]),
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 403


# ============================================================
# Job Synchronization Tests
# ============================================================

def test_work_in_progress_updates_job_status(client):
    """
    Starting Work should move the Job to in_progress.
    """

    data = setup_work(client)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    work_id = create_response.json()["id"]

    client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(data["worker_token"]),
        json={
            "status": "in_progress",
        },
    )

    response = client.get(
        f"/jobs/{data['job_id']}",
        headers=auth_headers(data["customer_token"]),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_completed_work_updates_job_status(client):
    """
    Completing Work should complete the Job.
    """

    data = setup_work(client)

    create_response = client.post(
        "/works/",
        headers=auth_headers(data["worker_token"]),
        json={
            "assignment_id": data["assignment_id"],
        },
    )

    work_id = create_response.json()["id"]

    client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(data["worker_token"]),
        json={
            "status": "in_progress",
        },
    )

    client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(data["worker_token"]),
        json={
            "status": "completed",
        },
    )

    response = client.get(
        f"/jobs/{data['job_id']}",
        headers=auth_headers(data["customer_token"]),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


# ============================================================
# Authentication Tests
# ============================================================

def test_create_work_requires_authentication(client):
    """
    Work creation requires authentication.
    """

    response = client.post(
        "/works/",
        json={
            "assignment_id": 1,
        },
    )

    assert response.status_code == 401


def test_get_work_requires_authentication(client):
    """
    Work viewing requires authentication.
    """

    response = client.get("/works/1")

    assert response.status_code == 401