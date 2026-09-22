from datetime import datetime, timedelta, timezone

import jwt

from backend.app.core.config import settings
from backend.app.core.security import create_access_token


def register_and_login(client):
    register_response = client.post(
        "/auth/register",
        json={
            "name": "JWT Test User",
            "email": "jwt-security@example.com",
            "password": "TestPassword123",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "jwt-security@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def test_valid_token_is_accepted(client):
    token = register_and_login(client)

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200


def test_expired_token_is_rejected(client):
    register_and_login(client)

    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc)
            - timedelta(minutes=1),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {expired_token}",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid or expired token"
    )


def test_invalid_signature_is_rejected(client):
    register_and_login(client)

    token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=30),
        },
        "wrong-secret-key-that-is-definitely-long-enough-for-hs384",
        algorithm=settings.algorithm,
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401


def test_malformed_token_is_rejected(client):
    register_and_login(client)

    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer this-is-not-a-jwt",
        },
    )

    assert response.status_code == 401


def test_wrong_algorithm_is_rejected(client):
    register_and_login(client)

    test_secret = "x" * 48

    token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=30),
        },
        test_secret,
        algorithm="HS384",
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401


def test_missing_subject_is_rejected(client):
    register_and_login(client)

    token = jwt.encode(
        {
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=30),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_invalid_subject_is_rejected(client):
    register_and_login(client)

    token = jwt.encode(
        {
            "sub": "not-an-integer",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=30),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401


def test_missing_authorization_header_is_rejected(client):
    register_and_login(client)

    response = client.get("/users/me")

    assert response.status_code == 401
