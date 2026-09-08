"""
Tests for MurphAI ML prediction API.
"""

from fastapi import status

from backend.app.api.ml import predict_worker_job
from backend.app.core.security import get_current_user_id
from backend.app.main import app


# ============================================================
# Test Data
# ============================================================


def valid_prediction_payload() -> dict:
    """
    Return valid raw worker-job data.
    """

    return {
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


# ============================================================
# Authentication
# ============================================================


def test_ml_prediction_requires_authentication(client):
    """
    ML prediction endpoint must require authentication.
    """

    response = client.post(
        "/ml/predict",
        json=valid_prediction_payload(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================
# Successful Prediction
# ============================================================


def test_ml_prediction_returns_200(client, monkeypatch):
    """
    Valid authenticated request should return 200.
    """

    def fake_prediction(request):
        return {
            "predicted_success": 1,
            "success_probability": 0.93,
            "model_name": "RandomForest",
        }

    monkeypatch.setattr(
        "backend.app.api.ml.predict_worker_job_success",
        fake_prediction,
    )

    app.dependency_overrides[get_current_user_id] = lambda: 1

    try:
        response = client.post(
            "/ml/predict",
            json=valid_prediction_payload(),
        )

        assert response.status_code == status.HTTP_200_OK

    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_ml_prediction_response_structure(client, monkeypatch):
    """
    Successful prediction should return the expected fields.
    """

    def fake_prediction(request):
        return {
            "predicted_success": 1,
            "success_probability": 0.93,
            "model_name": "RandomForest",
        }

    monkeypatch.setattr(
        "backend.app.api.ml.predict_worker_job_success",
        fake_prediction,
    )

    app.dependency_overrides[get_current_user_id] = lambda: 1

    try:
        response = client.post(
            "/ml/predict",
            json=valid_prediction_payload(),
        )

        data = response.json()

        assert "predicted_success" in data
        assert "success_probability" in data
        assert "model_name" in data

    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_ml_prediction_values_are_valid(client, monkeypatch):
    """
    Prediction values must satisfy the response contract.
    """

    def fake_prediction(request):
        return {
            "predicted_success": 1,
            "success_probability": 0.93,
            "model_name": "RandomForest",
        }

    monkeypatch.setattr(
        "backend.app.api.ml.predict_worker_job_success",
        fake_prediction,
    )

    app.dependency_overrides[get_current_user_id] = lambda: 1

    try:
        response = client.post(
            "/ml/predict",
            json=valid_prediction_payload(),
        )

        data = response.json()

        assert data["predicted_success"] in [0, 1]
        assert 0.0 <= data["success_probability"] <= 1.0
        assert data["model_name"] == "RandomForest"

    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


# ============================================================
# Request Validation
# ============================================================


def test_ml_prediction_rejects_negative_experience(client):
    """
    Worker experience cannot be negative.
    """

    app.dependency_overrides[get_current_user_id] = lambda: 1

    try:
        payload = valid_prediction_payload()
        payload["worker_experience_years"] = -1

        response = client.post(
            "/ml/predict",
            json=payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_ml_prediction_rejects_invalid_success_rate(client):
    """
    Success rate must be between 0 and 1.
    """

    app.dependency_overrides[get_current_user_id] = lambda: 1

    try:
        payload = valid_prediction_payload()
        payload["worker_success_rate"] = 1.5

        response = client.post(
            "/ml/predict",
            json=payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_ml_prediction_rejects_invalid_rating(client):
    """
    Worker rating must be between 0 and 5.
    """

    app.dependency_overrides[get_current_user_id] = lambda: 1

    try:
        payload = valid_prediction_payload()
        payload["worker_rating"] = 6.0

        response = client.post(
            "/ml/predict",
            json=payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_ml_prediction_rejects_zero_required_skills(client):
    """
    A job must require at least one skill.
    """

    app.dependency_overrides[get_current_user_id] = lambda: 1

    try:
        payload = valid_prediction_payload()
        payload["required_skill_count"] = 0

        response = client.post(
            "/ml/predict",
            json=payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_ml_prediction_rejects_negative_distance(client):
    """
    Distance cannot be negative.
    """

    app.dependency_overrides[get_current_user_id] = lambda: 1

    try:
        payload = valid_prediction_payload()
        payload["distance_km"] = -5.0

        response = client.post(
            "/ml/predict",
            json=payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    finally:
        app.dependency_overrides.pop(get_current_user_id, None)


def test_ml_prediction_rejects_extra_fields(client):
    """
    The request schema must reject unknown fields.
    """

    app.dependency_overrides[get_current_user_id] = lambda: 1

    try:
        payload = valid_prediction_payload()
        payload["unknown_field"] = "not_allowed"

        response = client.post(
            "/ml/predict",
            json=payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    finally:
        app.dependency_overrides.pop(get_current_user_id, None)