"""
Tests for the MurphAI champion inference layer.
"""

import pandas as pd
import pytest

from ml.src.inference.champion_predict import (
    load_champion_model,
    predict_with_champion,
)


# ============================================================
# Test Data
# ============================================================


def create_test_features() -> pd.DataFrame:
    """
    Create a valid feature row for inference.

    The columns must match the features used
    during model training.
    """

    return pd.DataFrame(
        [
            {
                "worker_experience_years": 5,
                "worker_completed_jobs": 30,
                "worker_success_rate": 0.90,
                "worker_rating": 4.7,
                "required_skill_count": 3,
                "matched_skill_count": 3,
                "skill_match_ratio": 1.0,
                "location_match": 1,
                "distance_km": 5.0,
                "job_complexity": 2,
                "job_budget": 5000.0,
                "worker_reliability_score": 0.90,
                "budget_per_complexity": 2500.0,
                "skill_gap": 0,
            }
        ]
    )


# ============================================================
# Tests
# ============================================================


def test_load_champion_model():
    """
    Champion model should load successfully.
    """

    model = load_champion_model()

    assert model is not None


def test_predict_with_champion_returns_result():
    """
    Champion inference should return a valid prediction result.
    """

    features = create_test_features()

    result = predict_with_champion(features)

    assert isinstance(result, dict)

    assert "predicted_success" in result
    assert "success_probability" in result
    assert "model_name" in result


def test_prediction_is_binary():
    """
    Predicted success should be either 0 or 1.
    """

    features = create_test_features()

    result = predict_with_champion(features)

    assert result["predicted_success"] in {0, 1}


def test_probability_is_valid():
    """
    Success probability must be between 0 and 1.
    """

    features = create_test_features()

    result = predict_with_champion(features)

    assert 0.0 <= result["success_probability"] <= 1.0


def test_champion_model_name():
    """
    The inference layer should identify the current champion.
    """

    features = create_test_features()

    result = predict_with_champion(features)

    assert result["model_name"] == "RandomForest"


def test_empty_features_are_rejected():
    """
    Empty input should raise a ValueError.
    """

    features = pd.DataFrame()

    with pytest.raises(ValueError):
        predict_with_champion(features)


def test_invalid_input_type_is_rejected():
    """
    Non-DataFrame input should raise a TypeError.
    """

    with pytest.raises(TypeError):
        predict_with_champion(
            {
                "worker_experience_years": 5
            }
        )