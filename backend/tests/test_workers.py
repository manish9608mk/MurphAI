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


def test_create_worker(client, db):
    user_id = create_test_user(
        db,
        "Worker One",
        "worker1@example.com",
    )

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

    data = response.json()

    assert data["user_id"] == user_id
    assert data["bio"] == "Experienced electrician"
    assert data["location"] == "Bhopal"
    assert data["experience_years"] == 5
    assert data["is_available"] is True


def test_create_worker_requires_authentication(client):
    response = client.post(
        "/workers/",
        json={
            "bio": "Experienced electrician",
            "location": "Bhopal",
            "experience_years": 5,
            "is_available": True,
        },
    )

    assert response.status_code == 401


def test_user_cannot_create_two_worker_profiles(client, db):
    user_id = create_test_user(
        db,
        "Worker Two",
        "worker2@example.com",
    )

    payload = {
        "bio": "Experienced plumber",
        "location": "Bhopal",
        "experience_years": 3,
        "is_available": True,
    }

    first_response = client.post(
        "/workers/",
        headers=auth_headers(user_id),
        json=payload,
    )

    second_response = client.post(
        "/workers/",
        headers=auth_headers(user_id),
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert (
        second_response.json()["detail"]
        == "Worker profile already exists for this user"
    )


def test_get_workers(client, db):
    user_id = create_test_user(
        db,
        "Worker Three",
        "worker3@example.com",
    )

    client.post(
        "/workers/",
        headers=auth_headers(user_id),
        json={
            "bio": "Electrician",
            "location": "Bhopal",
            "experience_years": 4,
            "is_available": True,
        },
    )

    response = client.get(
        "/workers/",
        headers=auth_headers(user_id),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_single_worker(client, db):
    user_id = create_test_user(
        db,
        "Worker Four",
        "worker4@example.com",
    )

    create_response = client.post(
        "/workers/",
        headers=auth_headers(user_id),
        json={
            "bio": "Mechanic",
            "location": "Bhopal",
            "experience_years": 6,
            "is_available": False,
        },
    )

    worker_id = create_response.json()["id"]

    response = client.get(
        f"/workers/{worker_id}",
        headers=auth_headers(user_id),
    )

    assert response.status_code == 200
    assert response.json()["id"] == worker_id


def test_other_user_can_view_worker(client, db):
    owner_id = create_test_user(
        db,
        "Worker Five",
        "worker5@example.com",
    )

    other_user_id = create_test_user(
        db,
        "Worker Viewer",
        "viewer@example.com",
    )

    create_response = client.post(
        "/workers/",
        headers=auth_headers(owner_id),
        json={
            "bio": "Technician",
            "location": "Bhopal",
            "experience_years": 7,
            "is_available": True,
        },
    )

    worker_id = create_response.json()["id"]

    response = client.get(
        f"/workers/{worker_id}",
        headers=auth_headers(other_user_id),
    )

    assert response.status_code == 200


def test_update_own_worker(client, db):
    user_id = create_test_user(
        db,
        "Worker Six",
        "worker6@example.com",
    )

    create_response = client.post(
        "/workers/",
        headers=auth_headers(user_id),
        json={
            "bio": "Electrician",
            "location": "Bhopal",
            "experience_years": 2,
            "is_available": True,
        },
    )

    worker_id = create_response.json()["id"]

    response = client.put(
        f"/workers/{worker_id}",
        headers=auth_headers(user_id),
        json={
            "bio": "Senior Electrician",
            "location": "Indore",
            "experience_years": 8,
            "is_available": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["bio"] == "Senior Electrician"
    assert data["location"] == "Indore"
    assert data["experience_years"] == 8
    assert data["is_available"] is False


def test_cannot_update_other_users_worker(client, db):
    owner_id = create_test_user(
        db,
        "Worker Seven",
        "worker7@example.com",
    )

    other_user_id = create_test_user(
        db,
        "Worker Eight",
        "worker8@example.com",
    )

    create_response = client.post(
        "/workers/",
        headers=auth_headers(owner_id),
        json={
            "bio": "Plumber",
            "location": "Bhopal",
            "experience_years": 5,
            "is_available": True,
        },
    )

    worker_id = create_response.json()["id"]

    response = client.put(
        f"/workers/{worker_id}",
        headers=auth_headers(other_user_id),
        json={
            "bio": "Hacked profile",
            "location": "Delhi",
            "experience_years": 20,
            "is_available": False,
        },
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == "You are not allowed to update this worker profile"
    )


def test_delete_own_worker(client, db):
    user_id = create_test_user(
        db,
        "Worker Nine",
        "worker9@example.com",
    )

    create_response = client.post(
        "/workers/",
        headers=auth_headers(user_id),
        json={
            "bio": "Car mechanic",
            "location": "Bhopal",
            "experience_years": 5,
            "is_available": True,
        },
    )

    worker_id = create_response.json()["id"]

    response = client.delete(
        f"/workers/{worker_id}",
        headers=auth_headers(user_id),
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/workers/{worker_id}",
        headers=auth_headers(user_id),
    )

    assert get_response.status_code == 404


def test_cannot_delete_other_users_worker(client, db):
    owner_id = create_test_user(
        db,
        "Worker Ten",
        "worker10@example.com",
    )

    other_user_id = create_test_user(
        db,
        "Worker Eleven",
        "worker11@example.com",
    )

    create_response = client.post(
        "/workers/",
        headers=auth_headers(owner_id),
        json={
            "bio": "Construction worker",
            "location": "Bhopal",
            "experience_years": 10,
            "is_available": True,
        },
    )

    worker_id = create_response.json()["id"]

    response = client.delete(
        f"/workers/{worker_id}",
        headers=auth_headers(other_user_id),
    )

    # Authenticated user, but not the owner.
    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == "You are not allowed to delete this worker profile"
    )


def test_worker_not_found(client, db):
    user_id = create_test_user(
        db,
        "Worker Twelve",
        "worker12@example.com",
    )

    response = client.get(
        "/workers/999999",
        headers=auth_headers(user_id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Worker not found"


def test_get_workers_requires_authentication(client):
    response = client.get("/workers/")

    assert response.status_code == 401


def test_get_single_worker_requires_authentication(client):
    response = client.get("/workers/1")

    assert response.status_code == 401