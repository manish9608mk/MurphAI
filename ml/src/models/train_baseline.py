"""
Train a baseline ML model for MurphAI worker-job matching.

This module:

    1. Loads the validated dataset.
    2. Creates ML features.
    3. Splits the dataset.
    4. Trains a Logistic Regression baseline.
    5. Evaluates the model on validation data.
    6. Tracks the experiment with MLflow.

The baseline model gives MurphAI a simple
performance benchmark before using more advanced models.
"""

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.src.data.data_loader import load_and_validate_dataset
from ml.src.data.dataset_split import split_dataset
from ml.src.features.feature_engineering import prepare_features
from ml.src.models.model_io import save_model
from ml.src.tracking.mlflow_tracking import (
    start_run,
    log_parameters,
    log_metrics,
    log_model,
)


# ============================================================
# Model Configuration
# ============================================================

RANDOM_STATE = 42

MAX_ITERATIONS = 1000


# ============================================================
# Model Creation
# ============================================================


def create_baseline_model() -> Pipeline:
    """
    Create the baseline Logistic Regression model.

    StandardScaler is used because Logistic Regression
    performs better when numerical features are on
    comparable scales.

    Returns
    -------
    Pipeline
        Scikit-learn pipeline containing scaling
        and Logistic Regression.
    """

    model = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    random_state=RANDOM_STATE,
                    max_iter=MAX_ITERATIONS,
                ),
            ),
        ]
    )

    return model


# ============================================================
# Model Evaluation
# ============================================================


def evaluate_model(
    model: Pipeline,
    X: pd.DataFrame,
    y: pd.Series,
) -> dict[str, float]:
    """
    Evaluate a trained classification model.

    Returns
    -------
    dict[str, float]
        Classification metrics.
    """

    predictions = model.predict(X)

    probabilities = model.predict_proba(X)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y, predictions),
        "precision": precision_score(y, predictions, zero_division=0),
        "recall": recall_score(y, predictions, zero_division=0),
        "f1": f1_score(y, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y, probabilities),
    }

    return metrics


# ============================================================
# Training
# ============================================================


def train_baseline_model() -> tuple[
    Pipeline,
    dict[str, float],
]:
    """
    Train and evaluate the baseline model.

    Returns
    -------
    tuple
        Trained model and validation metrics.
    """

    # --------------------------------------------------------
    # Step 1: Load and validate dataset
    # --------------------------------------------------------

    df = load_and_validate_dataset()

    # --------------------------------------------------------
    # Step 2: Feature engineering
    # --------------------------------------------------------

    X, y = prepare_features(df)

    # --------------------------------------------------------
    # Step 3: Train/validation/test split
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
    # Step 4: Create baseline model
    # --------------------------------------------------------

    model = create_baseline_model()

    # --------------------------------------------------------
    # Step 5: Start MLflow run
    # --------------------------------------------------------

    with start_run("logistic-regression-baseline"):

        # ----------------------------------------------------
        # Step 6: Log model parameters
        # ----------------------------------------------------

        log_parameters(
            {
                "model_type": "LogisticRegression",
                "random_state": RANDOM_STATE,
                "max_iterations": MAX_ITERATIONS,
                "scaler": "StandardScaler",
            }
        )

        # ----------------------------------------------------
        # Step 7: Train model
        # ----------------------------------------------------

        model.fit(X_train, y_train)

        # ----------------------------------------------------
        # Step 8: Evaluate on validation data
        # ----------------------------------------------------

        validation_metrics = evaluate_model(
            model,
            X_validation,
            y_validation,
        )

        # ----------------------------------------------------
        # Step 9: Log validation metrics to MLflow
        # ----------------------------------------------------

        log_metrics(validation_metrics)

        # ----------------------------------------------------
        # Step 10: Log trained model to MLflow
        # ----------------------------------------------------

        log_model(model)

        # ----------------------------------------------------
        # Step 11: Save model locally
        # ----------------------------------------------------

        model_path = save_model(model)

    print(f"\nModel saved to: {model_path}")

    # --------------------------------------------------------
    # Step 12: Print validation metrics
    # --------------------------------------------------------

    print("\nMurphAI Baseline Model")
    print("=" * 40)

    print(f"Training samples:   {len(X_train)}")
    print(f"Validation samples: {len(X_validation)}")
    print(f"Test samples:       {len(X_test)}")

    print("\nValidation Metrics")
    print("-" * 40)

    for metric_name, metric_value in validation_metrics.items():
        print(
            f"{metric_name.upper():<10}: "
            f"{metric_value:.4f}"
        )

    return model, validation_metrics


# ============================================================
# Script Entry Point
# ============================================================


if __name__ == "__main__":
    train_baseline_model()