# ============================================================
# Evidence Tests
# ============================================================

# These tests verify:
#
# 1. Worker can add evidence
# 2. Evidence can be viewed by worker
# 3. Evidence can be viewed by customer
# 4. Unrelated users cannot view evidence
# 5. Evidence cannot be added before Work starts
# 6. Invalid evidence types are rejected
# 7. Authentication is required
#


# ============================================================
# Helper Functions
# ============================================================

def create_user(client, name, email, password="password123"):
    """
    Create a user.
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
    Create an assignment.
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
    Worker accepts the assignment.
    """

    return client.patch(
        f"/assignments/{assignment_id}/accept",
        headers=auth_headers(token),
    )


def create_work(client, token, assignment_id):
    """
    Create Work for an accepted assignment.
    """

    return client.post(
        "/works/",
        headers=auth_headers(token),
        json={
            "assignment_id": assignment_id,
            "description": "Started electrical repair",
        },
    )


def start_work(client, token, work_id):
    """
    Move Work from pending to in_progress.
    """

    return client.patch(
        f"/works/{work_id}/status",
        headers=auth_headers(token),
        json={
            "status": "in_progress",
        },
    )


def setup_evidence(client):
    """
    Create the complete structure required for
    Evidence testing.

    Customer
        ↓
    Job
        ↓
    Assignment
        ↓
    Worker accepts
        ↓
    Work
        ↓
    Work becomes in_progress
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

    # --------------------------------------------------------
    # Create Work
    # --------------------------------------------------------

    work_response = create_work(
        client,
        worker_token,
        assignment_id,
    )

    assert work_response.status_code == 201

    work_id = work_response.json()["id"]

    # --------------------------------------------------------
    # Start Work
    # --------------------------------------------------------

    start_response = start_work(
        client,
        worker_token,
        work_id,
    )

    assert start_response.status_code == 200

    return {
        "customer_token": customer_token,
        "worker_token": worker_token,
        "job_id": job_id,
        "worker_id": worker_id,
        "assignment_id": assignment_id,
        "work_id": work_id,
    }


# ============================================================
# Create Evidence Tests
# ============================================================

def test_worker_can_create_evidence(client):
    """
    The assigned worker can add evidence to Work.
    """

    data = setup_evidence(client)

    response = client.post(
        "/evidence/",
        headers=auth_headers(data["worker_token"]),
        json={
            "work_id": data["work_id"],
            "evidence_type": "photo",
            "description": "Photo of completed wiring",
            "url": "https://example.com/wiring-photo.jpg",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["work_id"] == data["work_id"]
    assert body["evidence_type"] == "photo"
    assert body["description"] == "Photo of completed wiring"
    assert body["url"] == "https://example.com/wiring-photo.jpg"


def test_customer_cannot_create_evidence(client):
    """
    The customer cannot add evidence.

    Evidence must be submitted by the worker
    who actually performed the Work.
    """

    data = setup_evidence(client)

    response = client.post(
        "/evidence/",
        headers=auth_headers(data["customer_token"]),
        json={
            "work_id": data["work_id"],
            "evidence_type": "photo",
            "description": "Customer evidence",
            "url": "https://example.com/customer-photo.jpg",
        },
    )

    assert response.status_code == 403


def test_unrelated_user_cannot_create_evidence(client):
    """
    An unrelated user cannot add evidence.
    """

    data = setup_evidence(client)

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
        "/evidence/",
        headers=auth_headers(other_token),
        json={
            "work_id": data["work_id"],
            "evidence_type": "photo",
            "url": "https://example.com/photo.jpg",
        },
    )

    assert response.status_code == 403


# ============================================================
# Work Status Tests
# ============================================================

def test_evidence_cannot_be_added_before_work_starts(client):
    """
    Evidence cannot be added while Work is still pending.
    """

    # Create the basic structure manually so that
    # Work remains in the pending state.

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

    accept_response = accept_assignment(
        client,
        worker_token,
        assignment_id,
    )

    assert accept_response.status_code == 200

    work_response = create_work(
        client,
        worker_token,
        assignment_id,
    )

    assert work_response.status_code == 201

    work_id = work_response.json()["id"]

    # Work is still pending.

    response = client.post(
        "/evidence/",
        headers=auth_headers(worker_token),
        json={
            "work_id": work_id,
            "evidence_type": "photo",
            "url": "https://example.com/photo.jpg",
        },
    )

    assert response.status_code == 403


def test_worker_can_add_evidence_to_completed_work(client):
    """
    Evidence can also be added after Work is completed.
    """

    data = setup_evidence(client)

    # Complete the Work.

    response = client.patch(
        f"/works/{data['work_id']}/status",
        headers=auth_headers(data["worker_token"]),
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 200

    # Add evidence.

    response = client.post(
        "/evidence/",
        headers=auth_headers(data["worker_token"]),
        json={
            "work_id": data["work_id"],
            "evidence_type": "photo",
            "description": "Final proof",
            "url": "https://example.com/final-photo.jpg",
        },
    )

    assert response.status_code == 201


# ============================================================
# Evidence Type Tests
# ============================================================

def test_photo_evidence_allowed(client):
    """
    Photo evidence is allowed.
    """

    data = setup_evidence(client)

    response = client.post(
        "/evidence/",
        headers=auth_headers(data["worker_token"]),
        json={
            "work_id": data["work_id"],
            "evidence_type": "photo",
            "url": "https://example.com/photo.jpg",
        },
    )

    assert response.status_code == 201


def test_document_evidence_allowed(client):
    """
    Document evidence is allowed.
    """

    data = setup_evidence(client)

    response = client.post(
        "/evidence/",
        headers=auth_headers(data["worker_token"]),
        json={
            "work_id": data["work_id"],
            "evidence_type": "document",
            "url": "https://example.com/invoice.pdf",
        },
    )

    assert response.status_code == 201


def test_video_evidence_allowed(client):
    """
    Video evidence is allowed.
    """

    data = setup_evidence(client)

    response = client.post(
        "/evidence/",
        headers=auth_headers(data["worker_token"]),
        json={
            "work_id": data["work_id"],
            "evidence_type": "video",
            "url": "https://example.com/work-video.mp4",
        },
    )

    assert response.status_code == 201


def test_receipt_evidence_allowed(client):
    """
    Receipt evidence is allowed.
    """

    data = setup_evidence(client)

    response = client.post(
        "/evidence/",
        headers=auth_headers(data["worker_token"]),
        json={
            "work_id": data["work_id"],
            "evidence_type": "receipt",
            "url": "https://example.com/receipt.pdf",
        },
    )

    assert response.status_code == 201


def test_invalid_evidence_type_rejected(client):
    """
    Unknown evidence types are rejected.
    """

    data = setup_evidence(client)

    response = client.post(
        "/evidence/",
        headers=auth_headers(data["worker_token"]),
        json={
            "work_id": data["work_id"],
            "evidence_type": "random_type",
            "url": "https://example.com/file.jpg",
        },
    )

    assert response.status_code == 403


# ============================================================
# View Evidence Tests
# ============================================================

def test_worker_can_view_evidence(client):
    """
    The assigned worker can view evidence.
    """

    data = setup_evidence(client)

    create_response = client.post(
        "/evidence/",
        headers=auth_headers(data["worker_token"]),
        json={
            "work_id": data["work_id"],
            "evidence_type": "photo",
            "url": "https://example.com/photo.jpg",
        },
    )

    assert create_response.status_code == 201

    evidence_id = create_response.json()["id"]

    response = client.get(
        f"/evidence/{evidence_id}",
        headers=auth_headers(data["worker_token"]),
    )

    assert response.status_code == 200
    assert response.json()["id"] == evidence_id


def test_customer_can_view_evidence(client):
    """
    The customer can view evidence belonging
    to their Job.
    """

    data = setup_evidence(client)

    create_response = client.post(
        "/evidence/",
        headers=auth_headers(data["worker_token"]),
        json={
            "work_id": data["work_id"],
            "evidence_type": "photo",
            "url": "https://example.com/photo.jpg",
        },
    )

    evidence_id = create_response.json()["id"]

    response = client.get(
        f"/evidence/{evidence_id}",
        headers=auth_headers(data["customer_token"]),
    )

    assert response.status_code == 200
    assert response.json()["id"] == evidence_id


def test_unrelated_user_cannot_view_evidence(client):
    """
    An unrelated user cannot view evidence.
    """

    data = setup_evidence(client)

    create_response = client.post(
        "/evidence/",
        headers=auth_headers(data["worker_token"]),
        json={
            "work_id": data["work_id"],
            "evidence_type": "photo",
            "url": "https://example.com/photo.jpg",
        },
    )

    evidence_id = create_response.json()["id"]

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
        f"/evidence/{evidence_id}",
        headers=auth_headers(other_token),
    )

    assert response.status_code == 403


# ============================================================
# Authentication Tests
# ============================================================

def test_create_evidence_requires_authentication(client):
    """
    Creating evidence requires authentication.
    """

    response = client.post(
        "/evidence/",
        json={
            "work_id": 1,
            "evidence_type": "photo",
            "url": "https://example.com/photo.jpg",
        },
    )

    assert response.status_code == 401


def test_get_evidence_requires_authentication(client):
    """
    Viewing evidence requires authentication.
    """

    response = client.get("/evidence/1")

    assert response.status_code == 401