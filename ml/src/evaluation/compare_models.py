"""
Compare MurphAI baseline ML models.

This module compares:

    1. Logistic Regression
    2. Random Forest

Both models are evaluated on the same unseen test dataset.

The goal is to determine which model currently performs
better for the worker-job success prediction problem.
"""

from pathlib import Path

import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from ml.src.data.data_loader import load_and_validate_dataset
from ml.src.data.dataset_split import split_dataset
from ml.src.features.feature_engineering import prepare_features
from ml.src.models.model_io import load_model


# ============================================================
# Configuration
# ============================================================

BASELINE_MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "worker_job_baseline.joblib"
)

RANDOM_FOREST_MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "worker_job_random_forest.joblib"
)


# ============================================================
# Model Evaluation
# ============================================================


def evaluate_model(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """
    Evaluate a trained classification model.

    Parameters
    ----------
    model : object
        Trained classification model.

    X_test : pd.DataFrame
        Test feature matrix.

    y_test : pd.Series
        Test target values.

    Returns
    -------
    dict
        Model evaluation metrics.
    """

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities,
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
    }


# ============================================================
# Comparison
# ============================================================


def compare_models(
    baseline_metrics: dict,
    random_forest_metrics: dict,
) -> pd.DataFrame:
    """
    Create a comparison table for both models.

    Parameters
    ----------
    baseline_metrics : dict
        Metrics for Logistic Regression.

    random_forest_metrics : dict
        Metrics for Random Forest.

    Returns
    -------
    pd.DataFrame
        Comparison table.
    """

    comparison = pd.DataFrame(
        {
            "Logistic Regression": baseline_metrics,
            "Random Forest": random_forest_metrics,
        }
    )

    return comparison


# ============================================================
# Champion Selection
# ============================================================


def select_champion(
    baseline_metrics: dict,
    random_forest_metrics: dict,
) -> str:
    """
    Select the current champion model.

    F1 score is used as the primary selection metric.

    Parameters
    ----------
    baseline_metrics : dict
        Metrics for Logistic Regression.

    random_forest_metrics : dict
        Metrics for Random Forest.

    Returns
    -------
    str
        Name of the winning model.
    """

    baseline_f1 = baseline_metrics["f1"]

    random_forest_f1 = random_forest_metrics["f1"]

    if baseline_f1 >= random_forest_f1:
        return "Logistic Regression"

    return "Random Forest"


# ============================================================
# Main Comparison Pipeline
# ============================================================


def run_comparison() -> tuple[pd.DataFrame, str]:
    """
    Run the complete model comparison pipeline.

    Returns
    -------
    tuple
        Comparison DataFrame and champion model name.
    """

    # --------------------------------------------------------
    # Step 1: Load dataset
    # --------------------------------------------------------

    df = load_and_validate_dataset()

    # --------------------------------------------------------
    # Step 2: Prepare features
    # --------------------------------------------------------

    X, y = prepare_features(df)

    # --------------------------------------------------------
    # Step 3: Create identical dataset split
    # --------------------------------------------------------

    (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    ) = split_dataset(X, y)

    # --------------------------------------------------------
    # Step 4: Load Logistic Regression model
    # --------------------------------------------------------

    baseline_model = load_model(
        BASELINE_MODEL_PATH
    )

    # --------------------------------------------------------
    # Step 5: Load Random Forest model
    # --------------------------------------------------------

    random_forest_model = load_model(
        RANDOM_FOREST_MODEL_PATH
    )

    # --------------------------------------------------------
    # Step 6: Evaluate Logistic Regression
    # --------------------------------------------------------

    baseline_metrics = evaluate_model(
        model=baseline_model,
        X_test=X_test,
        y_test=y_test,
    )

    # --------------------------------------------------------
    # Step 7: Evaluate Random Forest
    # --------------------------------------------------------

    random_forest_metrics = evaluate_model(
        model=random_forest_model,
        X_test=X_test,
        y_test=y_test,
    )

    # --------------------------------------------------------
    # Step 8: Build comparison table
    # --------------------------------------------------------

    comparison = compare_models(
        baseline_metrics=baseline_metrics,
        random_forest_metrics=random_forest_metrics,
    )

    # --------------------------------------------------------
    # Step 9: Select champion
    # --------------------------------------------------------

    champion = select_champion(
        baseline_metrics=baseline_metrics,
        random_forest_metrics=random_forest_metrics,
    )

    return comparison, champion


# ============================================================
# CLI
# ============================================================


def main() -> None:
    """
    Run model comparison from the command line.
    """

    comparison, champion = run_comparison()

    print()
    print("MurphAI Model Comparison")
    print("=" * 50)

    print()
    print(
        comparison.to_string(
            float_format=lambda value: f"{value:.4f}"
        )
    )

    print()
    print("Champion Model")
    print("-" * 50)

    print(champion)


if __name__ == "__main__":
    main()