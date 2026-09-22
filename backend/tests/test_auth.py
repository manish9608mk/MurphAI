def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Manish",
            "email": "auth-test@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Manish"
    assert data["email"] == "auth-test@example.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_email_registration_is_rejected(client):
    payload = {
        "name": "Manish",
        "email": "duplicate-auth-test@example.com",
        "password": "TestPassword123",
    }

    first_response = client.post(
        "/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json={
            **payload,
            "name": "Another User",
        },
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "Email already registered"
    )
