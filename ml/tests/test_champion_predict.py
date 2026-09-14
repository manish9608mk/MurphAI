"""
Tests for the MurphAI champion inference layer.

These tests verify:

    1. Champion model loading.
    2. Champion prediction behavior.
    3. Prediction output validation.
    4. Feature validation.
    5. In-memory champion model caching.
    6. Explicit champion model cache clearing.
"""

import pandas as pd
import pytest

import ml.src.inference.champion_predict as champion_predict


# Test feature data

def create_test_features() -> pd.DataFrame:
    """
    Create a valid feature row for inference.

    The columns match the feature structure expected by
    the MurphAI champion model.
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


# Original champion inference tests

def test_load_champion_model():
    """
    Verify that the champion model can be loaded successfully.

    This test uses the real MLflow champion model so the
    inference layer is also verified against the configured
    development MLflow environment.
    """

    champion_predict.clear_champion_model_cache()

    model = champion_predict.load_champion_model()

    assert model is not None

    champion_predict.clear_champion_model_cache()


def test_predict_with_champion_returns_result():
    """
    Verify that champion inference returns a dictionary
    containing the expected prediction fields.
    """

    champion_predict.clear_champion_model_cache()

    features = create_test_features()

    result = champion_predict.predict_with_champion(
        features
    )

    assert isinstance(result, dict)

    assert "predicted_success" in result
    assert "success_probability" in result
    assert "model_name" in result

    champion_predict.clear_champion_model_cache()


def test_prediction_is_binary():
    """
    Verify that the predicted success value is binary.

    A binary prediction must be either:

        0 -> unsuccessful
        1 -> successful
    """

    champion_predict.clear_champion_model_cache()

    features = create_test_features()

    result = champion_predict.predict_with_champion(
        features
    )

    assert result["predicted_success"] in {0, 1}

    champion_predict.clear_champion_model_cache()


def test_probability_is_valid():
    """
    Verify that the success probability is between 0 and 1.
    """

    champion_predict.clear_champion_model_cache()

    features = create_test_features()

    result = champion_predict.predict_with_champion(
        features
    )

    assert 0.0 <= result["success_probability"] <= 1.0

    champion_predict.clear_champion_model_cache()


def test_champion_model_name():
    """
    Verify that the inference layer identifies the
    configured champion model correctly.
    """

    champion_predict.clear_champion_model_cache()

    features = create_test_features()

    result = champion_predict.predict_with_champion(
        features
    )

    assert result["model_name"] == "RandomForest"

    champion_predict.clear_champion_model_cache()


def test_empty_features_are_rejected():
    """
    Verify that empty feature input is rejected.
    """

    champion_predict.clear_champion_model_cache()

    features = pd.DataFrame()

    with pytest.raises(ValueError):
        champion_predict.predict_with_champion(
            features
        )

    champion_predict.clear_champion_model_cache()


def test_invalid_input_type_is_rejected():
    """
    Verify that non-DataFrame input is rejected before
    reaching the model.
    """

    champion_predict.clear_champion_model_cache()

    with pytest.raises(TypeError):
        champion_predict.predict_with_champion(
            {
                "worker_experience_years": 5
            }
        )

    champion_predict.clear_champion_model_cache()


# Test model caching

class FakeModel:
    """
    Small fake model used to test inference caching.

    The fake model implements only the methods required by
    predict_with_champion().
    """

    def predict(
        self,
        features: pd.DataFrame,
    ) -> list[int]:
        """
        Return a deterministic successful prediction.
        """

        return [1]

    def predict_proba(
        self,
        features: pd.DataFrame,
    ) -> list[list[float]]:
        """
        Return deterministic probabilities.

        Column 0 represents unsuccessful.
        Column 1 represents successful.
        """

        return [[0.07, 0.93]]


def test_champion_model_is_cached(monkeypatch):
    """
    Verify that the champion model is loaded only once.

    The first access loads the model from MLflow.
    Later accesses reuse the same model from memory.
    """

    load_count = 0
    fake_model = FakeModel()

    def fake_load_model(model_uri):
        """
        Simulate MLflow loading the champion model.
        """

        nonlocal load_count

        load_count += 1

        return fake_model

    monkeypatch.setattr(
        champion_predict.mlflow.sklearn,
        "load_model",
        fake_load_model,
    )

    # Always begin with an empty cache so test behavior
    # does not depend on another test's model state.
    champion_predict.clear_champion_model_cache()

    first_model = champion_predict.load_champion_model()
    second_model = champion_predict.load_champion_model()

    assert first_model is fake_model
    assert second_model is fake_model

    # The second access must use the in-memory cache.
    assert load_count == 1

    champion_predict.clear_champion_model_cache()


def test_clearing_champion_model_cache_allows_reload(monkeypatch):
    """
    Verify that clearing the cache forces the next access
    to load the champion model again.
    """

    load_count = 0

    def fake_load_model(model_uri):
        """
        Simulate a fresh model load from MLflow.
        """

        nonlocal load_count

        load_count += 1

        return FakeModel()

    monkeypatch.setattr(
        champion_predict.mlflow.sklearn,
        "load_model",
        fake_load_model,
    )

    champion_predict.clear_champion_model_cache()

    # First access loads the model.
    champion_predict.load_champion_model()

    assert load_count == 1

    # Second access uses the cached model.
    champion_predict.load_champion_model()

    assert load_count == 1

    # Clearing the cache simulates a future model refresh.
    champion_predict.clear_champion_model_cache()

    # The next access must load the model again.
    champion_predict.load_champion_model()

    assert load_count == 2

    champion_predict.clear_champion_model_cache()


def test_predict_with_champion_uses_cached_model(monkeypatch):
    """
    Verify that repeated predictions reuse the same
    in-memory champion model.
    """

    fake_model = FakeModel()
    load_count = 0

    def fake_load_model(model_uri):
        """
        Simulate one MLflow model load.
        """

        nonlocal load_count

        load_count += 1

        return fake_model

    monkeypatch.setattr(
        champion_predict.mlflow.sklearn,
        "load_model",
        fake_load_model,
    )

    champion_predict.clear_champion_model_cache()

    features = create_test_features()

    first_result = champion_predict.predict_with_champion(
        features
    )

    second_result = champion_predict.predict_with_champion(
        features
    )

    assert first_result["predicted_success"] == 1
    assert first_result["success_probability"] == 0.93
    assert first_result["model_name"] == "RandomForest"

    assert second_result["predicted_success"] == 1
    assert second_result["success_probability"] == 0.93
    assert second_result["model_name"] == "RandomForest"

    # Two predictions must require only one model load.
    assert load_count == 1

    champion_predict.clear_champion_model_cache()