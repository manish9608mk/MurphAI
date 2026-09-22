def register_and_login(client, name, email, password):
    # Register
    register_response = client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


# =========================
# GET OWN USER
# =========================

def test_get_own_user(client):
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    response = client.get(
        "/users/1",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Manish"
    assert data["email"] == "manish@example.com"


# =========================
# CANNOT GET OTHER USER
# =========================

def test_cannot_get_other_user(client):
    # User 1
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    # User 2
    client.post(
        "/auth/register",
        json={
            "name": "Rahul",
            "email": "rahul@example.com",
            "password": "TestPassword123",
        },
    )

    response = client.get(
        "/users/2",
        headers=headers,
    )

    assert response.status_code == 403

    data = response.json()

    assert data["detail"] == (
        "You are not allowed to access this user"
    )


# =========================
# UPDATE OWN USER
# =========================

def test_update_own_user(client):
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    response = client.put(
        "/users/1",
        headers=headers,
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


# =========================
# CANNOT UPDATE OTHER USER
# =========================

def test_cannot_update_other_user(client):
    # User 1
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    # User 2
    client.post(
        "/auth/register",
        json={
            "name": "Rahul",
            "email": "rahul@example.com",
            "password": "TestPassword123",
        },
    )

    response = client.put(
        "/users/2",
        headers=headers,
        json={
            "name": "Hacked User",
            "email": "hacked@example.com",
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["detail"] == (
        "You are not allowed to update this user"
    )


# =========================
# DELETE OWN USER
# =========================

def test_delete_own_user(client):
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    response = client.delete(
        "/users/1",
        headers=headers,
    )

    assert response.status_code == 204

    response = client.get(
        "/users/1",
        headers=headers,
    )

    assert response.status_code == 404


# =========================
# CANNOT DELETE OTHER USER
# =========================

def test_cannot_delete_other_user(client):
    # User 1
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    # User 2
    client.post(
        "/auth/register",
        json={
            "name": "Rahul",
            "email": "rahul@example.com",
            "password": "TestPassword123",
        },
    )

    response = client.delete(
        "/users/2",
        headers=headers,
    )

    assert response.status_code == 403

    data = response.json()

    assert data["detail"] == (
        "You are not allowed to delete this user"
    )


# =========================
# USER NOT FOUND
# =========================

def test_get_user_not_found(client):
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    response = client.get(
        "/users/999",
        headers=headers,
    )

    assert response.status_code == 403