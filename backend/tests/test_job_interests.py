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
    is_available: bool = True,
):
    response = client.post(
        "/workers/",
        headers=auth_headers(user_id),
        json={
            "bio": "Experienced electrician",
            "location": "Bhopal",
            "experience_years": 5,
            "is_available": is_available,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_job(
    client,
    customer_id: int,
    status: str = "open",
):
    response = client.post(
        "/jobs/",
        headers=auth_headers(customer_id),
        json={
            "title": "Fix Electrical Wiring",
            "description": (
                "Need an electrician to repair "
                "wiring in my house."
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


def test_worker_can_express_interest(
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
    )

    response = client.post(
        "/job-interests/",
        headers=auth_headers(worker_user_id),
        json={
            "job_id": job_id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["job_id"] == job_id
    assert data["status"] == "pending"


def test_worker_cannot_duplicate_pending_interest(
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

    job_id = create_job(
        client,
        customer_id,
    )

    payload = {
        "job_id": job_id,
    }

    first_response = client.post(
        "/job-interests/",
        headers=auth_headers(worker_user_id),
        json=payload,
    )

    second_response = client.post(
        "/job-interests/",
        headers=auth_headers(worker_user_id),
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_worker_can_withdraw_interest(
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

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/job-interests/",
        headers=auth_headers(worker_user_id),
        json={
            "job_id": job_id,
        },
    )

    interest_id = create_response.json()["id"]

    response = client.patch(
        f"/job-interests/{interest_id}/withdraw",
        headers=auth_headers(worker_user_id),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "withdrawn"


def test_withdrawn_interest_can_be_submitted_again(
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
        "worker4@example.com",
    )

    create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/job-interests/",
        headers=auth_headers(worker_user_id),
        json={
            "job_id": job_id,
        },
    )

    interest_id = create_response.json()["id"]

    withdraw_response = client.patch(
        f"/job-interests/{interest_id}/withdraw",
        headers=auth_headers(worker_user_id),
    )

    assert withdraw_response.status_code == 200

    reapply_response = client.post(
        "/job-interests/",
        headers=auth_headers(worker_user_id),
        json={
            "job_id": job_id,
        },
    )

    assert reapply_response.status_code == 201
    assert reapply_response.json()["id"] == interest_id
    assert reapply_response.json()["status"] == "pending"


def test_unavailable_worker_cannot_express_interest(
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
        "Unavailable Worker",
        "unavailable@example.com",
    )

    create_worker(
        client,
        worker_user_id,
        is_available=False,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    response = client.post(
        "/job-interests/",
        headers=auth_headers(worker_user_id),
        json={
            "job_id": job_id,
        },
    )

    assert response.status_code == 400


def test_worker_cannot_express_interest_in_own_job(
    client,
    db,
):
    user_id = create_test_user(
        db,
        "Worker Customer",
        "sameuser@example.com",
    )

    create_worker(
        client,
        user_id,
    )

    job_id = create_job(
        client,
        user_id,
    )

    response = client.post(
        "/job-interests/",
        headers=auth_headers(user_id),
        json={
            "job_id": job_id,
        },
    )

    assert response.status_code == 403


def test_cannot_express_interest_in_closed_job(
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
        "worker6@example.com",
    )

    create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
        status="cancelled",
    )

    response = client.post(
        "/job-interests/",
        headers=auth_headers(worker_user_id),
        json={
            "job_id": job_id,
        },
    )

    assert response.status_code == 400


def test_customer_can_view_job_interests(
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
        "worker7@example.com",
    )

    create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    client.post(
        "/job-interests/",
        headers=auth_headers(worker_user_id),
        json={
            "job_id": job_id,
        },
    )

    response = client.get(
        f"/jobs/{job_id}/interests",
        headers=auth_headers(customer_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["job_id"] == job_id
    assert data[0]["status"] == "pending"


def test_other_customer_cannot_view_job_interests(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Eight",
        "customer8@example.com",
    )

    other_customer_id = create_test_user(
        db,
        "Other Customer",
        "othercustomer@example.com",
    )

    worker_user_id = create_test_user(
        db,
        "Worker Eight",
        "worker8@example.com",
    )

    create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    response = client.get(
        f"/jobs/{job_id}/interests",
        headers=auth_headers(other_customer_id),
    )

    assert response.status_code == 403


def test_worker_cannot_withdraw_another_workers_interest(
    client,
    db,
):
    customer_id = create_test_user(
        db,
        "Customer Nine",
        "customer9@example.com",
    )

    worker_one_id = create_test_user(
        db,
        "Worker Nine",
        "worker9@example.com",
    )

    worker_two_id = create_test_user(
        db,
        "Worker Ten",
        "worker10@example.com",
    )

    create_worker(
        client,
        worker_one_id,
    )

    create_worker(
        client,
        worker_two_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    create_response = client.post(
        "/job-interests/",
        headers=auth_headers(worker_one_id),
        json={
            "job_id": job_id,
        },
    )

    interest_id = create_response.json()["id"]

    response = client.patch(
        f"/job-interests/{interest_id}/withdraw",
        headers=auth_headers(worker_two_id),
    )

    assert response.status_code == 403


def test_worker_can_view_own_interests(
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
        "Worker Eleven",
        "worker11@example.com",
    )

    create_worker(
        client,
        worker_user_id,
    )

    job_id = create_job(
        client,
        customer_id,
    )

    client.post(
        "/job-interests/",
        headers=auth_headers(worker_user_id),
        json={
            "job_id": job_id,
        },
    )

    response = client.get(
        "/job-interests/mine",
        headers=auth_headers(worker_user_id),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_job_interest_requires_authentication(
    client,
):
    response = client.post(
        "/job-interests/",
        json={
            "job_id": 1,
        },
    )

    assert response.status_code == 401