from backend.app.models.confirmation import Confirmation


def register_user(client, name, email, password="password123"):
    response = client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    return response.json()


def login_user(client, email, password="password123"):
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
    return {
        "Authorization": f"Bearer {token}",
    }


def create_job(client, token):
    response = client.post(
        "/jobs/",
        headers=auth_headers(token),
        json={
            "title": "Electrical Repair",
            "description": "Repair electrical wiring",
            "location": "Bhopal",
            "budget": 1500,
        },
    )

    assert response.status_code == 201

    return response.json()


def create_worker(client, token):
    response = client.post(
        "/workers/",
        headers=auth_headers(token),
        json={
            "bio": "Experienced electrician",
            "location": "Bhopal",
            "experience_years": 5,
            "is_available": True,
        },
    )

    assert response.status_code == 201

    return response.json()


def create_accepted_assignment(client, customer_token, worker_token):
    job = create_job(client, customer_token)
    worker = create_worker(client, worker_token)

    response = client.post(
        "/assignments/",
        headers=auth_headers(customer_token),
        json={
            "job_id": job["id"],
            "worker_id": worker["id"],
        },
    )

    assert response.status_code == 201

    assignment_id = response.json()["id"]

    response = client.patch(
        f"/assignments/{assignment_id}/accept",
        headers=auth_headers(worker_token),
    )

    assert response.status_code == 200

    return assignment_id


def create_completed_work(client, customer_token, worker_token):
    assignment_id = create_accepted_assignment(
        client,
        customer_token,
        worker_token,
    )

    response = client.post(
        "/works/",
        headers=auth_headers(worker_token),
        json={
            "assignment_id": assignment_id,
            "description": "Electrical repair completed",
        },
    )

    assert response.status_code == 201

    work_id = response.json()["id"]

    response = client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(worker_token),
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200

    response = client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(worker_token),
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 200

    return work_id


# ============================================================
# Create Confirmation
# ============================================================

def test_customer_can_confirm_completed_work(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    work_id = create_completed_work(
        client,
        customer_token,
        worker_token,
    )

    response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "Work completed successfully",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["work_id"] == work_id
    assert data["comment"] == "Work completed successfully"


# ============================================================
# Worker Cannot Confirm
# ============================================================

def test_worker_cannot_confirm_work(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    work_id = create_completed_work(
        client,
        customer_token,
        worker_token,
    )

    response = client.post(
        "/confirmations/",
        headers=auth_headers(worker_token),
        json={
            "work_id": work_id,
            "comment": "I confirm my own work",
        },
    )

    assert response.status_code == 403


# ============================================================
# Cannot Confirm Incomplete Work
# ============================================================

def test_cannot_confirm_incomplete_work(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    assignment_id = create_accepted_assignment(
        client,
        customer_token,
        worker_token,
    )

    response = client.post(
        "/works/",
        headers=auth_headers(worker_token),
        json={
            "assignment_id": assignment_id,
            "description": "Work not completed yet",
        },
    )

    assert response.status_code == 201

    work_id = response.json()["id"]

    response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "Trying too early",
        },
    )

    assert response.status_code == 403


# ============================================================
# Duplicate Confirmation
# ============================================================

def test_duplicate_confirmation_is_rejected(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    work_id = create_completed_work(
        client,
        customer_token,
        worker_token,
    )

    first_response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "First confirmation",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "Second confirmation",
        },
    )

    assert second_response.status_code == 403


# ============================================================
# Get Confirmation
# ============================================================

def test_customer_can_view_confirmation(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    work_id = create_completed_work(
        client,
        customer_token,
        worker_token,
    )

    response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "Looks good",
        },
    )

    assert response.status_code == 201

    confirmation_id = response.json()["id"]

    response = client.get(
        f"/confirmations/{confirmation_id}",
        headers=auth_headers(customer_token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == confirmation_id


def test_worker_can_view_confirmation(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    work_id = create_completed_work(
        client,
        customer_token,
        worker_token,
    )

    response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "Looks good",
        },
    )

    assert response.status_code == 201

    confirmation_id = response.json()["id"]

    response = client.get(
        f"/confirmations/{confirmation_id}",
        headers=auth_headers(worker_token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == confirmation_id


# ============================================================
# Unauthorized User
# ============================================================

def test_unrelated_user_cannot_view_confirmation(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    register_user(
        client,
        "Other User",
        "other@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    other_token = login_user(
        client,
        "other@example.com",
    )

    work_id = create_completed_work(
        client,
        customer_token,
        worker_token,
    )

    response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "Looks good",
        },
    )

    assert response.status_code == 201

    confirmation_id = response.json()["id"]

    response = client.get(
        f"/confirmations/{confirmation_id}",
        headers=auth_headers(other_token),
    )

    assert response.status_code == 403


# ============================================================
# Missing Work
# ============================================================

def test_confirmation_for_missing_work_is_rejected(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": 9999,
            "comment": "Missing work",
        },
    )

    assert response.status_code == 403


# ============================================================
# Database Verification
# ============================================================

def test_confirmation_is_saved_in_database(
    client,
    db,
):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    work_id = create_completed_work(
        client,
        customer_token,
        worker_token,
    )

    response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "Database test",
        },
    )

    assert response.status_code == 201

    confirmation = (
        db.query(Confirmation)
        .filter(Confirmation.work_id == work_id)
        .first()
    )

    assert confirmation is not None
    assert confirmation.work_id == work_id
    assert confirmation.comment == "Database test"

def test_customer_can_get_confirmation_for_work(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    work_id = create_completed_work(
        client,
        customer_token,
        worker_token,
    )

    create_response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "Confirmed",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/confirmations/work/{work_id}",
        headers=auth_headers(customer_token),
    )

    assert response.status_code == 200
    assert response.json()["work_id"] == work_id


def test_worker_can_get_confirmation_for_work(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    work_id = create_completed_work(
        client,
        customer_token,
        worker_token,
    )

    create_response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "Confirmed",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/confirmations/work/{work_id}",
        headers=auth_headers(worker_token),
    )

    assert response.status_code == 200
    assert response.json()["work_id"] == work_id


def test_unrelated_user_cannot_get_confirmation_for_work(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    register_user(
        client,
        "Other User",
        "other-confirmation@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    other_token = login_user(
        client,
        "other-confirmation@example.com",
    )

    work_id = create_completed_work(
        client,
        customer_token,
        worker_token,
    )

    create_response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/confirmations/work/{work_id}",
        headers=auth_headers(other_token),
    )

    assert response.status_code == 403


def test_get_confirmation_for_work_requires_existing_confirmation(
    client,
):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    register_user(
        client,
        "Worker",
        "worker@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    worker_token = login_user(
        client,
        "worker@example.com",
    )

    work_id = create_completed_work(
        client,
        customer_token,
        worker_token,
    )

    response = client.get(
        f"/confirmations/work/{work_id}",
        headers=auth_headers(customer_token),
    )

    assert response.status_code == 403