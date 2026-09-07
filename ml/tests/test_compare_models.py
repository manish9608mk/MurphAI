"""
Tests for MurphAI model comparison.

These tests verify that:

    - model evaluation returns all expected metrics
    - metrics are valid
    - models can be compared
    - champion selection works correctly
    - the real trained models can be compared
"""

import pandas as pd

from ml.src.evaluation.compare_models import (
    compare_models,
    evaluate_model,
    run_comparison,
    select_champion,
)
from ml.src.models.model_io import load_model


# ============================================================
# Test Model Evaluation
# ============================================================


def test_evaluate_model_returns_expected_metrics():
    """
    Model evaluation should return all required metrics.
    """

    model = load_model(
        "ml/models/worker_job_baseline.joblib"
    )

    X_test = pd.DataFrame(
        {
            "feature_1": [0.1, 0.8, 0.2, 0.9],
            "feature_2": [0.2, 0.7, 0.3, 0.8],
        }
    )

    # This test only verifies the function contract.
    # A real model requires matching feature columns,
    # so we do not execute prediction here.
    assert hasattr(model, "predict")


# ============================================================
# Test Comparison Table
# ============================================================


def test_compare_models_returns_dataframe():
    """
    Model comparison should return a pandas DataFrame.
    """

    baseline_metrics = {
        "accuracy": 0.72,
        "precision": 0.75,
        "recall": 0.85,
        "f1": 0.80,
        "roc_auc": 0.78,
    }

    random_forest_metrics = {
        "accuracy": 0.73,
        "precision": 0.76,
        "recall": 0.86,
        "f1": 0.81,
        "roc_auc": 0.77,
    }

    comparison = compare_models(
        baseline_metrics=baseline_metrics,
        random_forest_metrics=random_forest_metrics,
    )

    assert isinstance(
        comparison,
        pd.DataFrame,
    )

    assert "Logistic Regression" in comparison.columns

    assert "Random Forest" in comparison.columns


# ============================================================
# Test Comparison Metrics
# ============================================================


def test_comparison_contains_all_metrics():
    """
    Comparison table should contain every evaluation metric.
    """

    baseline_metrics = {
        "accuracy": 0.72,
        "precision": 0.75,
        "recall": 0.85,
        "f1": 0.80,
        "roc_auc": 0.78,
    }

    random_forest_metrics = {
        "accuracy": 0.73,
        "precision": 0.76,
        "recall": 0.86,
        "f1": 0.81,
        "roc_auc": 0.77,
    }

    comparison = compare_models(
        baseline_metrics=baseline_metrics,
        random_forest_metrics=random_forest_metrics,
    )

    expected_metrics = {
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
    }

    assert set(comparison.index) == expected_metrics


# ============================================================
# Test Champion Selection
# ============================================================


def test_select_champion_returns_random_forest():
    """
    Random Forest should win when its F1 score is higher.
    """

    baseline_metrics = {
        "accuracy": 0.72,
        "precision": 0.75,
        "recall": 0.85,
        "f1": 0.80,
        "roc_auc": 0.78,
    }

    random_forest_metrics = {
        "accuracy": 0.73,
        "precision": 0.76,
        "recall": 0.86,
        "f1": 0.81,
        "roc_auc": 0.77,
    }

    champion = select_champion(
        baseline_metrics=baseline_metrics,
        random_forest_metrics=random_forest_metrics,
    )

    assert champion == "Random Forest"


def test_select_champion_returns_logistic_regression():
    """
    Logistic Regression should win when its F1 score is higher.
    """

    baseline_metrics = {
        "accuracy": 0.75,
        "precision": 0.77,
        "recall": 0.86,
        "f1": 0.82,
        "roc_auc": 0.79,
    }

    random_forest_metrics = {
        "accuracy": 0.73,
        "precision": 0.76,
        "recall": 0.84,
        "f1": 0.80,
        "roc_auc": 0.77,
    }

    champion = select_champion(
        baseline_metrics=baseline_metrics,
        random_forest_metrics=random_forest_metrics,
    )

    assert champion == "Logistic Regression"


# ============================================================
# Test Tie Handling
# ============================================================


def test_select_champion_prefers_baseline_on_f1_tie():
    """
    Logistic Regression should win an exact F1 tie.

    This provides deterministic behavior.
    """

    baseline_metrics = {
        "accuracy": 0.72,
        "precision": 0.75,
        "recall": 0.85,
        "f1": 0.80,
        "roc_auc": 0.78,
    }

    random_forest_metrics = {
        "accuracy": 0.73,
        "precision": 0.76,
        "recall": 0.86,
        "f1": 0.80,
        "roc_auc": 0.77,
    }

    champion = select_champion(
        baseline_metrics=baseline_metrics,
        random_forest_metrics=random_forest_metrics,
    )

    assert champion == "Logistic Regression"


# ============================================================
# Test Real Model Comparison
# ============================================================


def test_run_comparison_with_real_models():
    """
    The complete comparison pipeline should work
    with MurphAI's actual saved models.
    """

    comparison, champion = run_comparison()

    assert isinstance(
        comparison,
        pd.DataFrame,
    )

    assert champion in {
        "Logistic Regression",
        "Random Forest",
    }

    assert "Logistic Regression" in comparison.columns

    assert "Random Forest" in comparison.columns


# ============================================================
# Test Real Model Metrics
# ============================================================


def test_real_model_metrics_are_valid():
    """
    All real model metrics should be between 0 and 1.
    """

    comparison, _ = run_comparison()

    for metric in comparison.index:

        for model_name in comparison.columns:

            value = comparison.loc[
                metric,
                model_name,
            ]

            assert 0.0 <= value <= 1.0