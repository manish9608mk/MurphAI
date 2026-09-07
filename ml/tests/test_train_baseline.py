"""
Tests for the MurphAI baseline ML model.
"""

import pandas as pd
import pytest

from sklearn.pipeline import Pipeline

from ml.src.models.train_baseline import (
    create_baseline_model,
    evaluate_model,
    train_baseline_model,
)


# ============================================================
# Test Model Creation
# ============================================================


def test_create_baseline_model_returns_pipeline():
    """
    The baseline model should be a scikit-learn Pipeline.
    """

    model = create_baseline_model()

    assert isinstance(model, Pipeline)


def test_baseline_model_has_scaler_and_classifier():
    """
    The pipeline should contain both feature scaling
    and Logistic Regression.
    """

    model = create_baseline_model()

    assert "scaler" in model.named_steps
    assert "classifier" in model.named_steps

    assert model.named_steps["classifier"].__class__.__name__ == (
        "LogisticRegression"
    )


# ============================================================
# Test Model Training
# ============================================================


def test_baseline_model_can_train():
    """
    The baseline model should successfully train
    on a small dataset.
    """

    X = pd.DataFrame(
        {
            "feature_1": [1, 2, 3, 4, 5, 6],
            "feature_2": [2, 3, 4, 5, 6, 7],
        }
    )

    y = pd.Series([0, 0, 1, 1, 1, 0])

    model = create_baseline_model()

    model.fit(X, y)

    predictions = model.predict(X)

    assert len(predictions) == len(y)


# ============================================================
# Test Model Evaluation
# ============================================================


def test_evaluate_model_returns_expected_metrics():
    """
    Evaluation should return all required classification metrics.
    """

    X = pd.DataFrame(
        {
            "feature_1": [1, 2, 3, 4, 5, 6],
            "feature_2": [2, 3, 4, 5, 6, 7],
        }
    )

    y = pd.Series([0, 0, 1, 1, 1, 0])

    model = create_baseline_model()

    model.fit(X, y)

    metrics = evaluate_model(
        model,
        X,
        y,
    )

    expected_metrics = {
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
    }

    assert set(metrics.keys()) == expected_metrics


def test_evaluate_model_metrics_are_valid():
    """
    Classification metrics should be between 0 and 1.
    """

    X = pd.DataFrame(
        {
            "feature_1": [1, 2, 3, 4, 5, 6],
            "feature_2": [2, 3, 4, 5, 6, 7],
        }
    )

    y = pd.Series([0, 0, 1, 1, 1, 0])

    model = create_baseline_model()

    model.fit(X, y)

    metrics = evaluate_model(
        model,
        X,
        y,
    )

    for metric_name, metric_value in metrics.items():
        assert 0.0 <= metric_value <= 1.0


# ============================================================
# Test Full Training Pipeline
# ============================================================


def test_train_baseline_model_returns_model_and_metrics():
    """
    The complete baseline training pipeline should
    return a trained model and validation metrics.
    """

    model, metrics = train_baseline_model()

    assert isinstance(model, Pipeline)

    assert isinstance(metrics, dict)

    assert {
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
    } == set(metrics.keys())


def test_train_baseline_model_metrics_are_valid():
    """
    Full pipeline metrics should be valid probabilities.
    """

    _, metrics = train_baseline_model()

    for metric_value in metrics.values():
        assert 0.0 <= metric_value <= 1.0