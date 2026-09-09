"""
Integration tests for MurphAI ML prediction API.

These tests verify:

    1. Authenticated users can call /ml/predict.
    2. The API returns a valid ML prediction.
    3. Unauthenticated requests are rejected.
    4. Invalid request data is rejected.
"""

from backend.app.core.security import create_access_token


# ============================================================
# Test Data
# ============================================================


VALID_REQUEST = {
    "worker_experience_years": 5,
    "worker_completed_jobs": 30,
    "worker_success_rate": 0.90,
    "worker_rating": 4.7,
    "required_skill_count": 3,
    "matched_skill_count": 3,
    "location_match": 1,
    "distance_km": 5.0,
    "job_complexity": 2,
    "job_budget": 5000.0,
}


def get_auth_headers() -> dict[str, str]:
    """
    Create authentication headers for an API request.
    """

    token = create_access_token(
        user_id=1
    )

    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================
# Successful Prediction
# ============================================================


def test_ml_prediction_success(client):
    """
    Verify that an authenticated request
    returns a successful ML prediction.
    """

    response = client.post(
        "/ml/predict",
        json=VALID_REQUEST,
        headers=get_auth_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert "predicted_success" in data
    assert "success_probability" in data
    assert "model_name" in data

    assert data["predicted_success"] in [0, 1]

    assert (
        0.0
        <= data["success_probability"]
        <= 1.0
    )

    assert data["model_name"] == "RandomForest"


# ============================================================
# Authentication
# ============================================================


def test_ml_prediction_requires_authentication(client):
    """
    Verify that unauthenticated requests are rejected.
    """

    response = client.post(
        "/ml/predict",
        json=VALID_REQUEST,
    )

    assert response.status_code == 401


# ============================================================
# Invalid Input
# ============================================================


def test_ml_prediction_rejects_invalid_input(client):
    """
    Verify that invalid request data is rejected
    by Pydantic validation.
    """

    invalid_request = {
        **VALID_REQUEST,
        "worker_success_rate": 2.0,
    }

    response = client.post(
        "/ml/predict",
        json=invalid_request,
        headers=get_auth_headers(),
    )

    assert response.status_code == 422