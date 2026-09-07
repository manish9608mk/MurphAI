"""
Evaluation utilities for the MurphAI baseline model.

This module evaluates the trained worker-job matching model
using the unseen test dataset.

It provides:

    - Accuracy
    - Precision
    - Recall
    - F1 score
    - ROC-AUC
    - Confusion matrix
    - Classification report
    - Feature importance

The evaluation is performed on the test set so that the
final model performance is measured on data that was not
used during training.
"""

from pathlib import Path

import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
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

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "worker_job_baseline.joblib"
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
    Evaluate a trained classification model on test data.

    Parameters
    ----------
    model : object
        Trained scikit-learn classification model.

    X_test : pd.DataFrame
        Test feature matrix.

    y_test : pd.Series
        Test target values.

    Returns
    -------
    dict
        Dictionary containing classification metrics
        and diagnostic information.
    """

    # --------------------------------------------------------
    # Generate predictions
    # --------------------------------------------------------

    predictions = model.predict(X_test)

    # --------------------------------------------------------
    # Generate prediction probabilities
    # --------------------------------------------------------

    if not hasattr(model, "predict_proba"):
        raise ValueError(
            "The provided model does not support "
            "probability predictions."
        )

    probabilities = model.predict_proba(X_test)[:, 1]

    # --------------------------------------------------------
    # Classification metrics
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    confusion = confusion_matrix(
        y_test,
        predictions,
    )

    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    report = classification_report(
        y_test,
        predictions,
        zero_division=0,
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "confusion_matrix": confusion,
        "classification_report": report,
    }


# ============================================================
# Feature Importance
# ============================================================


def get_feature_importance(
    model,
    feature_names: list[str],
) -> pd.DataFrame:
    """
    Extract feature importance from a trained model.

    Supported model types:

    1. Tree-based models
       Uses feature_importances_.

    2. Linear models
       Uses the absolute value of coef_.

    3. Pipelines
       Attempts to inspect the final estimator inside
       the pipeline.

    Parameters
    ----------
    model : object
        Trained scikit-learn model.

    feature_names : list[str]
        Names of the model input features.

    Returns
    -------
    pd.DataFrame
        Feature names and importance values sorted from
        highest to lowest importance.
    """

    # --------------------------------------------------------
    # Check whether the model is a Pipeline
    # --------------------------------------------------------

    estimator = model

    if hasattr(model, "steps"):
        estimator = model.steps[-1][1]

    # --------------------------------------------------------
    # Tree-based models
    # --------------------------------------------------------

    if hasattr(estimator, "feature_importances_"):

        importance_values = estimator.feature_importances_

    # --------------------------------------------------------
    # Linear models
    # --------------------------------------------------------

    elif hasattr(estimator, "coef_"):

        coefficients = estimator.coef_

        if coefficients.ndim == 1:
            importance_values = abs(coefficients)

        else:
            importance_values = abs(coefficients[0])

    # --------------------------------------------------------
    # Unsupported model
    # --------------------------------------------------------

    else:
        raise ValueError(
            "The provided model does not expose "
            "feature_importances_ or coef_. "
            f"Loaded model type: {type(estimator).__name__}"
        )

    # --------------------------------------------------------
    # Validate feature count
    # --------------------------------------------------------

    if len(feature_names) != len(importance_values):
        raise ValueError(
            "Number of feature names does not match "
            "number of model importance values."
        )

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importance_values,
        }
    )

    # --------------------------------------------------------
    # Sort by importance
    # --------------------------------------------------------

    return importance.sort_values(
        by="importance",
        ascending=False,
        ignore_index=True,
    )


# ============================================================
# Complete Evaluation Pipeline
# ============================================================


def run_evaluation() -> dict:
    """
    Run the complete baseline model evaluation pipeline.

    Pipeline:

        Dataset
            ↓
        Feature Engineering
            ↓
        Train / Validation / Test Split
            ↓
        Load Saved Model
            ↓
        Test Evaluation
            ↓
        Feature Importance

    Returns
    -------
    dict
        Complete evaluation results.
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
    # Step 3: Split dataset
    # --------------------------------------------------------

    (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    ) = split_dataset(
        X,
        y,
    )

    # --------------------------------------------------------
    # Step 4: Load trained model
    # --------------------------------------------------------

    model = load_model(MODEL_PATH)

    # --------------------------------------------------------
    # Step 5: Evaluate model
    # --------------------------------------------------------

    results = evaluate_model(
        model=model,
        X_test=X_test,
        y_test=y_test,
    )

    # --------------------------------------------------------
    # Step 6: Extract feature importance
    # --------------------------------------------------------

    feature_importance = get_feature_importance(
        model=model,
        feature_names=list(X.columns),
    )

    results["feature_importance"] = feature_importance

    # --------------------------------------------------------
    # Additional information
    # --------------------------------------------------------

    results["test_samples"] = len(X_test)
    results["train_samples"] = len(X_train)
    results["validation_samples"] = len(X_validation)

    return results


# ============================================================
# CLI
# ============================================================


def main() -> None:
    """
    Run baseline model evaluation from the command line.
    """

    results = run_evaluation()

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    print()
    print("MurphAI Baseline Model Evaluation")
    print("=" * 40)

    # --------------------------------------------------------
    # Dataset information
    # --------------------------------------------------------

    print()
    print("Dataset")
    print("-" * 40)

    print(
        f"Training samples    : "
        f"{results['train_samples']}"
    )

    print(
        f"Validation samples  : "
        f"{results['validation_samples']}"
    )

    print(
        f"Test samples        : "
        f"{results['test_samples']}"
    )

    # --------------------------------------------------------
    # Test metrics
    # --------------------------------------------------------

    print()
    print("Test Metrics")
    print("-" * 40)

    print(
        f"ACCURACY  : "
        f"{results['accuracy']:.4f}"
    )

    print(
        f"PRECISION : "
        f"{results['precision']:.4f}"
    )

    print(
        f"RECALL    : "
        f"{results['recall']:.4f}"
    )

    print(
        f"F1        : "
        f"{results['f1']:.4f}"
    )

    print(
        f"ROC_AUC   : "
        f"{results['roc_auc']:.4f}"
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    print()
    print("Confusion Matrix")
    print("-" * 40)

    print(
        results["confusion_matrix"]
    )

    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    print()
    print("Classification Report")
    print("-" * 40)

    print(
        results["classification_report"]
    )

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    print()
    print("Feature Importance")
    print("-" * 40)

    print(
        results["feature_importance"].to_string(
            index=False
        )
    )


# ============================================================
# Entry Point
# ============================================================


if __name__ == "__main__":
    main()