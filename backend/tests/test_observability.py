from uuid import UUID

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_request_id_header_is_returned():
    response = client.get("/health")

    assert response.status_code == 200

    request_id = response.headers.get("X-Request-ID")

    assert request_id is not None
    assert len(request_id) == 36


def test_request_id_is_uuid():
    response = client.get("/health")

    request_id = response.headers["X-Request-ID"]

    UUID(request_id)


def test_request_id_is_unique():
    first_response = client.get("/health")
    second_response = client.get("/health")

    first_request_id = first_response.headers["X-Request-ID"]
    second_request_id = second_response.headers["X-Request-ID"]

    assert first_request_id != second_request_id
