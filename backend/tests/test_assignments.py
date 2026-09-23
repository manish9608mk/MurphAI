# ============================================================
# Job Assignment Tests
# ============================================================
#
# These tests verify the relationship between:
#
# Customer
#     ↓
# Job
#     ↓
# Assignment
#     ↓
# Worker
#
# Main flow:
#
# OPEN Job
#     ↓
# PENDING Assignment
#     ↓
# Worker accepts
#     ↓
# ACCEPTED Assignment
#     ↓
# Job becomes ASSIGNED
#
# ============================================================


from backend.app.core.security import create_access_token
from backend.app.models.user import User


# ------------------------------------------------------------
# Helper: Create a test user
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Helper: Authentication headers
# ------------------------------------------------------------

def auth_headers(user_id: int):
    token = create_access_token(user_id)

    return {
        "Authorization": f"Bearer {token}",
    }


# ------------------------------------------------------------
# Helper: Create a worker
# ------------------------------------------------------------

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

    return response.json()["id"]


# ------------------------------------------------------------
# Helper: Create a job
# ------------------------------------------------------------

def create_job(
    client,
    user_id: int,
):
    response = client.post(
        "/jobs/",
        headers=auth_headers(user_id),
        json={
            "title": "Fix electrical wiring",
            "description": "Need an electrician to fix wiring.",
            "location": "Bhopal",
            "budget": 5000,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


# ============================================================
# TEST 1
# Customer can create an assignment
# ============================================================

def test_customer_can_create_assignment(
    client,
    db,
):
    # Create customer.
    customer_id = create_test_user(
        db,
        "Customer One",
        "customer1@example.com",
    )

    # Create worker.
    worker_user_id = create_test_user(
        db,
        "Worker One",
        "assignmentworker1@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    # Customer creates a job.
    job_id = create_job(
        client,
        customer_id,
    )

    # Customer assigns the worker.
    response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    # Assignment should be created.
    assert response.status_code == 201

    data = response.json()

    assert data["job_id"] == job_id
    assert data["worker_id"] == worker_id
    assert data["status"] == "pending"


# ============================================================
# TEST 2
# Assignment starts in PENDING state
# ============================================================

def test_assignment_starts_as_pending(
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
        "assignmentworker2@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assert response.status_code == 201

    # Newly created assignments must wait
    # for the worker's decision.
    assert response.json()["status"] == "pending"


# ============================================================
# TEST 3
# Worker can accept an assignment
# ============================================================

def test_worker_can_accept_assignment(
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
        "assignmentworker3@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    # Customer creates assignment.
    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assignment_id = create_response.json()["id"]

    # Worker accepts it.
    response = client.patch(
        f"/assignments/{assignment_id}/accept",
        headers=auth_headers(worker_user_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "accepted"


# ============================================================
# TEST 4
# Accepting assignment changes Job to ASSIGNED
# ============================================================

def test_accepting_assignment_assigns_job(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Four",
        "customer4@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Four",
        "assignmentworker4@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assignment_id = create_response.json()["id"]

    # Worker accepts assignment.
    response = client.patch(
        f"/assignments/{assignment_id}/accept",
        headers=auth_headers(worker_user_id),
    )

    assert response.status_code == 200

    # Now check the job.
    job_response = client.get(
        f"/jobs/{job_id}",
        headers=auth_headers(customer_id),
    )

    assert job_response.status_code == 200

    # Job should now be ASSIGNED.
    assert job_response.json()["status"] == "assigned"


# ============================================================
# TEST 5
# Worker can reject an assignment
# ============================================================

def test_worker_can_reject_assignment(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Five",
        "customer5@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Five",
        "assignmentworker5@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assignment_id = create_response.json()["id"]

    # Worker rejects assignment.
    response = client.patch(
        f"/assignments/{assignment_id}/reject",
        headers=auth_headers(worker_user_id),
    )

    assert response.status_code == 200

    assert response.json()["status"] == "rejected"


# ============================================================
# TEST 6
# Rejected assignment does not assign the job
# ============================================================

def test_rejected_assignment_keeps_job_open(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Six",
        "customer6@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Six",
        "assignmentworker6@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assignment_id = create_response.json()["id"]

    client.patch(
        f"/assignments/{assignment_id}/reject",
        headers=auth_headers(worker_user_id),
    )

    # Job should remain OPEN.
    job_response = client.get(
        f"/jobs/{job_id}",
        headers=auth_headers(customer_id),
    )

    assert job_response.status_code == 200
    assert job_response.json()["status"] == "open"


# ============================================================
# TEST 7
# Customer can cancel a pending assignment
# ============================================================

def test_customer_can_cancel_assignment(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Seven",
        "customer7@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Seven",
        "assignmentworker7@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assignment_id = create_response.json()["id"]

    # Customer cancels the assignment.
    response = client.patch(
        f"/assignments/{assignment_id}/cancel",
        headers=auth_headers(customer_id),
    )

    assert response.status_code == 200

    assert response.json()["status"] == "cancelled"


# ============================================================
# TEST 8
# Worker cannot accept another worker's assignment
# ============================================================

def test_other_worker_cannot_accept_assignment(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Eight",
        "customer8@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Eight",
        "assignmentworker8@example.com",
    )

    other_worker_user_id = create_test_user(
        db,
        "Other Worker",
        "otherworker@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    create_worker(
        client,
        other_worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assignment_id = create_response.json()["id"]

    # Wrong worker tries to accept it.
    response = client.patch(
        f"/assignments/{assignment_id}/accept",
        headers=auth_headers(other_worker_user_id),
    )

    assert response.status_code == 403


# ============================================================
# TEST 9
# Another customer cannot cancel the assignment
# ============================================================

def test_other_customer_cannot_cancel_assignment(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Nine",
        "customer9@example.com",
    )

    other_customer_id = create_test_user(
        db,
        "Other Customer",
        "othercustomer@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Nine",
        "assignmentworker9@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assignment_id = create_response.json()["id"]

    # Wrong customer tries to cancel.
    response = client.patch(
        f"/assignments/{assignment_id}/cancel",
        headers=auth_headers(other_customer_id),
    )

    assert response.status_code == 403


# ============================================================
# TEST 10
# Same worker cannot be assigned twice to the same job
# ============================================================

def test_same_worker_cannot_be_assigned_twice(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Ten",
        "customer10@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Ten",
        "assignmentworker10@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    payload = {
        "job_id": job_id,
        "worker_id": worker_id,
    }

    # First assignment.
    first_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json=payload,
    )

    # Second assignment.
    second_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


# ============================================================
# TEST 11
# Cannot assign a worker to a job owned by another customer
# ============================================================

def test_customer_cannot_assign_worker_to_other_users_job(
    client,
    db,
):
    job_owner_id = create_test_user(
        db,
        "Job Owner",
        "jobowner@example.com",
    )

    other_customer_id = create_test_user(
        db,
        "Other Customer Two",
        "othercustomer2@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Eleven",
        "assignmentworker11@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        job_owner_id,
    )

    # Wrong customer tries to assign the worker.
    response = client.post(
        "/assignments/",
        headers=auth_headers(other_customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assert response.status_code == 403


# ============================================================
# TEST 12
# Cannot assign an unavailable worker
# ============================================================

def test_cannot_assign_unavailable_worker(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Twelve",
        "customer12@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Unavailable Worker",
        "unavailableworker@example.com",
    )

    # Create worker as unavailable.
    response = client.post(
        "/workers/",
        headers=auth_headers(worker_user_id),
        json={
            "bio": "Unavailable electrician",
            "location": "Bhopal",
            "experience_years": 5,
            "is_available": False,
        },
    )

    assert response.status_code == 201

    worker_id = response.json()["id"]

    job_id = create_job(
        client,
        customer_id,
    )

    # Try to assign unavailable worker.
    response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assert response.status_code == 400


# ============================================================
# TEST 13
# Cannot create assignment for a non-existent job
# ============================================================

def test_assignment_job_not_found(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Thirteen",
        "customer13@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Thirteen",
        "assignmentworker13@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": 999999,
            "worker_id": worker_id,
        },
    )

    assert response.status_code == 404


# ============================================================
# TEST 14
# Cannot create assignment for a non-existent worker
# ============================================================

def test_assignment_worker_not_found(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Fourteen",
        "customer14@example.com",
    )

    job_id = create_job(
        client,
        customer_id,
    )

    response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": 999999,
        },
    )

    assert response.status_code == 404


# ============================================================
# TEST 15
# Unauthenticated user cannot create assignment
# ============================================================

def test_create_assignment_requires_authentication(
    client,
):
    response = client.post(
        "/assignments/",
        json={
            "job_id": 1,
            "worker_id": 1,
        },
    )

    assert response.status_code == 401


# ============================================================
# TEST 16
# Unauthenticated user cannot accept assignment
# ============================================================

def test_accept_assignment_requires_authentication(
    client,
):
    response = client.patch(
        "/assignments/1/accept",
    )

    assert response.status_code == 401


# ============================================================
# TEST 17
# Worker cannot accept the same assignment twice
# ============================================================

def test_worker_cannot_accept_assignment_twice(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Fifteen",
        "customer15@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Fifteen",
        "assignmentworker15@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assignment_id = create_response.json()["id"]

    # First acceptance.
    first_response = client.patch(
        f"/assignments/{assignment_id}/accept",
        headers=auth_headers(worker_user_id),
    )

    # Second acceptance should fail because
    # the assignment is already accepted.
    second_response = client.patch(
        f"/assignments/{assignment_id}/accept",
        headers=auth_headers(worker_user_id),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400


# ============================================================
# TEST 18
# Worker cannot reject an already accepted assignment
# ============================================================

def test_worker_cannot_reject_accepted_assignment(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Sixteen",
        "customer16@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Sixteen",
        "assignmentworker16@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assignment_id = create_response.json()["id"]

    # Accept first.
    accept_response = client.patch(
        f"/assignments/{assignment_id}/accept",
        headers=auth_headers(worker_user_id),
    )

    assert accept_response.status_code == 200

    # Then try to reject it.
    reject_response = client.patch(
        f"/assignments/{assignment_id}/reject",
        headers=auth_headers(worker_user_id),
    )

    assert reject_response.status_code == 400


# ============================================================
# TEST 19
# Assignment can be fetched by a participant
# ============================================================

def test_participant_can_view_assignment(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Seventeen",
        "customer17@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Seventeen",
        "assignmentworker17@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assignment_id = create_response.json()["id"]

    # Customer should be able to view it.
    response = client.get(
        f"/assignments/{assignment_id}",
        headers=auth_headers(customer_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == assignment_id
    assert data["job_id"] == job_id
    assert data["worker_id"] == worker_id


# ============================================================
# TEST 20
# Unrelated user cannot view assignment
# ============================================================

def test_unrelated_user_cannot_view_assignment(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Eighteen",
        "customer18@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Eighteen",
        "assignmentworker18@example.com",
    )

    unrelated_user_id = create_test_user(
        db,
        "Unrelated User",
        "unrelated@example.com",
    )

    worker_id = create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assignment_id = create_response.json()["id"]

    # Completely unrelated user tries to view it.
    response = client.get(
        f"/assignments/{assignment_id}",
        headers=auth_headers(unrelated_user_id),
    )

    assert response.status_code == 403

# ============================================================
# TEST 21
# Another worker cannot reject another worker's assignment
# ============================================================

def test_other_worker_cannot_reject_assignment(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Twenty One",
        "customer21@example.com",
    )

    assigned_worker_id = create_test_user(
        db,
        "Assigned Worker",
        "assignedworker21@example.com",
    )

    other_worker_id = create_test_user(
        db,
        "Other Worker Twenty One",
        "otherworker21@example.com",
    )

    worker_id = create_worker(
        client,
        assigned_worker_id,
    )

    create_worker(
        client,
        other_worker_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/assignments/",
        headers=auth_headers(customer_id),
        json={
            "job_id": job_id,
            "worker_id": worker_id,
        },
    )

    assert create_response.status_code == 201

    assignment_id = create_response.json()["id"]

    response = client.patch(
        f"/assignments/{assignment_id}/reject",
        headers=auth_headers(other_worker_id),
    )

    assert response.status_code == 403
