# to run pytest use this command: PYTHONPATH=. pytest

def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "name": "Manish",
            "email": "manish@example.com",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Manish"
    assert data["email"] == "manish@example.com"
    assert "id" in data

def test_get_users(client):
    client.post(
        "/users/",
        json={
            "name": "Manish",
            "email": "manish@example.com",
        },
    )

    response = client.get("/users/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Manish"
    assert data[0]["email"] == "manish@example.com"
    assert data[0]["id"] == 1


def test_get_single_user(client):
    # Create user first
    client.post(
        "/users/",
        json={
            "name": "Rahul",
            "email": "rahul@example.com",
        },
    )

    # Get user with ID 1
    response = client.get("/users/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Rahul"
    assert data["email"] == "rahul@example.com"

def test_get_user_not_found(client):
    response = client.get("/users/999")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "User not found"


def test_duplicate_email(client):
    client.post(
        "/users/",
        json={
            "name": "Manish",
            "email": "duplicate@example.com",
        },
    )

    response = client.post(
        "/users/",
        json={
            "name": "Rahul",
            "email": "duplicate@example.com",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"] == "Email already registered"


def test_update_user(client):
    # Create user
    client.post(
        "/users/",
        json={
            "name": "Manish",
            "email": "manish@example.com",
        },
    )

    # Update user
    response = client.put(
        "/users/1",
        json={
            "name": "Manish Kumar",
            "email": "manishkumar@example.com",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Manish Kumar"
    assert data["email"] == "manishkumar@example.com"


def test_delete_user(client):
    # Create user
    client.post(
        "/users/",
        json={
            "name": "Manish",
            "email": "manish@example.com",
        },
    )

    # Delete user
    response = client.delete("/users/1")

    assert response.status_code == 204

    # Verify user no longer exists
    response = client.get("/users/1")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "User not found"