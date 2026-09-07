"""
Tests for MurphAI inference pipeline.
"""

from pathlib import Path

import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from ml.src.inference.predict import (
    load_model,
    predict_success,
)


# ============================================================
# Test Data
# ============================================================

def create_test_interaction():
    """
    Create a valid worker-job interaction for testing.
    """

    return {
        "worker_experience_years": 5,
        "worker_completed_jobs": 42,
        "worker_success_rate": 0.88,
        "worker_rating": 4.6,
        "required_skill_count": 5,
        "matched_skill_count": 4,
        "skill_match_ratio": 0.8,
        "location_match": 1,
        "distance_km": 3.5,
        "job_complexity": 3,
        "job_budget": 2500,
    }


def create_test_model():
    """
    Create a small trained model for testing inference.

    This avoids depending on the real saved model
    inside individual unit tests.
    """

    X = pd.DataFrame(
        [
            {
                "worker_experience_years": 1,
                "worker_completed_jobs": 5,
                "worker_success_rate": 0.50,
                "worker_rating": 2.5,
                "required_skill_count": 5,
                "matched_skill_count": 2,
                "skill_match_ratio": 0.4,
                "location_match": 0,
                "distance_km": 25,
                "job_complexity": 5,
                "job_budget": 1000,
                "skill_gap": 3,
                "worker_reliability_score": 0.25,
                "budget_per_complexity": 200,
            },
            {
                "worker_experience_years": 8,
                "worker_completed_jobs": 100,
                "worker_success_rate": 0.95,
                "worker_rating": 4.9,
                "required_skill_count": 5,
                "matched_skill_count": 5,
                "skill_match_ratio": 1.0,
                "location_match": 1,
                "distance_km": 2,
                "job_complexity": 2,
                "job_budget": 5000,
                "skill_gap": 0,
                "worker_reliability_score": 0.931,
                "budget_per_complexity": 2500,
            },
        ]
    )

    y = [0, 1]

    model = LogisticRegression()

    model.fit(X, y)

    return model


# ============================================================
# Tests
# ============================================================


def test_load_model_returns_trained_model():
    """
    The real saved model should load successfully.
    """

    model = load_model()

    assert model is not None
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")


def test_load_model_missing_file_raises_error(tmp_path):
    """
    Loading a non-existent model should raise FileNotFoundError.
    """

    missing_model_path = (
        tmp_path / "missing_model.joblib"
    )

    with pytest.raises(FileNotFoundError):
        load_model(missing_model_path)


def test_predict_success_returns_expected_keys():
    """
    Prediction result should contain the expected fields.
    """

    model = create_test_model()

    result = predict_success(
        create_test_interaction(),
        model=model,
    )

    assert "success_probability" in result
    assert "predicted_success" in result


def test_success_probability_is_valid():
    """
    Success probability must be between 0 and 1.
    """

    model = create_test_model()

    result = predict_success(
        create_test_interaction(),
        model=model,
    )

    assert 0.0 <= result["success_probability"] <= 1.0


def test_prediction_is_binary():
    """
    Prediction must be either 0 or 1.
    """

    model = create_test_model()

    result = predict_success(
        create_test_interaction(),
        model=model,
    )

    assert result["predicted_success"] in {0, 1}


def test_prediction_is_numeric():
    """
    Prediction output should use numeric Python types.
    """

    model = create_test_model()

    result = predict_success(
        create_test_interaction(),
        model=model,
    )

    assert isinstance(
        result["success_probability"],
        float,
    )

    assert isinstance(
        result["predicted_success"],
        int,
    )


def test_prediction_with_real_saved_model():
    """
    The complete inference pipeline should work
    with MurphAI's actual saved baseline model.
    """

    result = predict_success(
        create_test_interaction()
    )

    assert 0.0 <= result["success_probability"] <= 1.0
    assert result["predicted_success"] in {0, 1}