# Payment Tests

from backend.app.models.payment import Payment


def register_user(client, name, email, password="password123"):
    response = client.post(
        "/users/",
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


def create_accepted_assignment(
    client,
    customer_token,
    worker_token,
):
    job = create_job(
        client,
        customer_token,
    )

    worker = create_worker(
        client,
        worker_token,
    )

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


def create_completed_work(
    client,
    customer_token,
    worker_token,
):
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


def confirm_work(
    client,
    customer_token,
    work_id,
):
    response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "Work completed successfully",
        },
    )

    assert response.status_code == 201

    return response.json()


# Create Payment

def test_customer_can_create_payment(client):
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

    confirm_work(
        client,
        customer_token,
        work_id,
    )

    response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "transaction_reference": "TEST-123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["work_id"] == work_id
    assert data["amount"] == 1500
    assert data["status"] == "pending"
    assert data["transaction_reference"] == "TEST-123"


# Payment Requires Confirmation

def test_payment_requires_confirmation(client):
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
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
        },
    )

    assert response.status_code == 403


# Worker Cannot Create Payment

def test_worker_cannot_create_payment(client):
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

    confirm_work(
        client,
        customer_token,
        work_id,
    )

    response = client.post(
        "/payments/",
        headers=auth_headers(worker_token),
        json={
            "work_id": work_id,
        },
    )

    assert response.status_code == 403


# Duplicate Payment

def test_duplicate_payment_is_rejected(client):
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

    confirm_work(
        client,
        customer_token,
        work_id,
    )

    first_response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
        },
    )

    assert second_response.status_code == 403


# Payment Must Be For Completed Work

def test_payment_requires_completed_work(client):
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
            "description": "Work still pending",
        },
    )

    assert response.status_code == 201

    work_id = response.json()["id"]

    confirm_response = client.post(
        "/confirmations/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "comment": "Too early",
        },
    )

    assert confirm_response.status_code == 403

    payment_response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
        },
    )

    assert payment_response.status_code == 403


# Client Cannot Control Payment Amount

def test_client_cannot_control_payment_amount(client):
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

    confirm_work(
        client,
        customer_token,
        work_id,
    )

    response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "amount": 1,
        },
    )

    assert response.status_code == 422


# Mark Payment As Paid

def test_customer_can_mark_payment_as_paid(client):
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

    confirm_work(
        client,
        customer_token,
        work_id,
    )

    response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
        },
    )

    assert response.status_code == 201

    payment_id = response.json()["id"]

    response = client.patch(
        f"/payments/{payment_id}/paid",
        headers=auth_headers(customer_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "paid"
    assert data["paid_at"] is not None


# Worker Cannot Mark Payment As Paid

def test_worker_cannot_mark_payment_as_paid(client):
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

    confirm_work(
        client,
        customer_token,
        work_id,
    )

    response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
        },
    )

    assert response.status_code == 201

    payment_id = response.json()["id"]

    response = client.patch(
        f"/payments/{payment_id}/paid",
        headers=auth_headers(worker_token),
    )

    assert response.status_code == 403


# Duplicate Paid Transition

def test_payment_cannot_be_marked_paid_twice(client):
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

    confirm_work(
        client,
        customer_token,
        work_id,
    )

    response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
        },
    )

    assert response.status_code == 201

    payment_id = response.json()["id"]

    response = client.patch(
        f"/payments/{payment_id}/paid",
        headers=auth_headers(customer_token),
    )

    assert response.status_code == 200

    response = client.patch(
        f"/payments/{payment_id}/paid",
        headers=auth_headers(customer_token),
    )

    assert response.status_code == 403


# Get Payment

def test_customer_can_view_payment(client):
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

    confirm_work(
        client,
        customer_token,
        work_id,
    )

    response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
        },
    )

    assert response.status_code == 201

    payment_id = response.json()["id"]

    response = client.get(
        f"/payments/{payment_id}",
        headers=auth_headers(customer_token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == payment_id


def test_worker_can_view_payment(client):
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

    confirm_work(
        client,
        customer_token,
        work_id,
    )

    response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
        },
    )

    assert response.status_code == 201

    payment_id = response.json()["id"]

    response = client.get(
        f"/payments/{payment_id}",
        headers=auth_headers(worker_token),
    )

    assert response.status_code == 200
    assert response.json()["id"] == payment_id


# Unauthorized User

def test_unrelated_user_cannot_view_payment(client):
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

    confirm_work(
        client,
        customer_token,
        work_id,
    )

    response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
        },
    )

    assert response.status_code == 201

    payment_id = response.json()["id"]

    response = client.get(
        f"/payments/{payment_id}",
        headers=auth_headers(other_token),
    )

    assert response.status_code == 403


# Missing Payment

def test_missing_payment_is_rejected(client):
    register_user(
        client,
        "Customer",
        "customer@example.com",
    )

    customer_token = login_user(
        client,
        "customer@example.com",
    )

    response = client.get(
        "/payments/9999",
        headers=auth_headers(customer_token),
    )

    assert response.status_code == 403


# Database Verification

def test_payment_is_saved_in_database(client, db):
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

    confirm_work(
        client,
        customer_token,
        work_id,
    )

    response = client.post(
        "/payments/",
        headers=auth_headers(customer_token),
        json={
            "work_id": work_id,
            "transaction_reference": "DB-TEST-123",
        },
    )

    assert response.status_code == 201

    payment = (
        db.query(Payment)
        .filter(
            Payment.work_id == work_id
        )
        .first()
    )

    assert payment is not None
    assert payment.work_id == work_id
    assert payment.amount == 1500
    assert payment.status == "pending"
    assert payment.transaction_reference == "DB-TEST-123"