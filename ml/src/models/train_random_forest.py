"""
Train the MurphAI Random Forest baseline model.

This module trains a Random Forest classifier for the
worker-job matching problem.

The model predicts whether a worker-job interaction
is likely to be successful.

Pipeline:

    Dataset
        ↓
    Feature Engineering
        ↓
    Train / Validation / Test Split
        ↓
    Random Forest Training
        ↓
    Validation Evaluation
        ↓
    Save Model
"""

from pathlib import Path

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
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
from ml.src.models.model_io import save_model


# ============================================================
# Configuration
# ============================================================

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "worker_job_random_forest.joblib"
)


# ============================================================
# Model Configuration
# ============================================================

RANDOM_STATE = 42

N_ESTIMATORS = 200

MAX_DEPTH = 10

MIN_SAMPLES_SPLIT = 5

MIN_SAMPLES_LEAF = 2


# ============================================================
# Model Training
# ============================================================


def create_random_forest_model() -> RandomForestClassifier:
    """
    Create the Random Forest classifier.

    Returns
    -------
    RandomForestClassifier
        Configured Random Forest model.
    """

    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        min_samples_split=MIN_SAMPLES_SPLIT,
        min_samples_leaf=MIN_SAMPLES_LEAF,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    return model


def train_random_forest_model() -> tuple[
    RandomForestClassifier,
    pd.DataFrame,
    pd.Series,
]:
    """
    Train the Random Forest model.

    Returns
    -------
    tuple
        Trained model, validation features, and validation target.
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
    ) = split_dataset(X, y)

    # --------------------------------------------------------
    # Step 4: Create model
    # --------------------------------------------------------

    model = create_random_forest_model()

    # --------------------------------------------------------
    # Step 5: Train model
    # --------------------------------------------------------

    model.fit(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # Step 6: Save model
    # --------------------------------------------------------

    model_path = save_model(
        model,
        MODEL_PATH,
    )

    print()
    print(f"Random Forest model saved to: {model_path}")

    return (
        model,
        X_validation,
        y_validation,
    )


# ============================================================
# Validation
# ============================================================


def evaluate_validation_set(
    model: RandomForestClassifier,
    X_validation: pd.DataFrame,
    y_validation: pd.Series,
) -> dict:
    """
    Evaluate the Random Forest model on validation data.

    Parameters
    ----------
    model : RandomForestClassifier
        Trained Random Forest model.

    X_validation : pd.DataFrame
        Validation feature matrix.

    y_validation : pd.Series
        Validation target values.

    Returns
    -------
    dict
        Validation metrics.
    """

    predictions = model.predict(
        X_validation
    )

    probabilities = model.predict_proba(
        X_validation
    )[:, 1]

    accuracy = accuracy_score(
        y_validation,
        predictions,
    )

    precision = precision_score(
        y_validation,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_validation,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_validation,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_validation,
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
# Main
# ============================================================


def main() -> None:
    """
    Train and evaluate the Random Forest model.
    """

    # --------------------------------------------------------
    # Train model
    # --------------------------------------------------------

    (
        model,
        X_validation,
        y_validation,
    ) = train_random_forest_model()

    # --------------------------------------------------------
    # Evaluate model
    # --------------------------------------------------------

    metrics = evaluate_validation_set(
        model=model,
        X_validation=X_validation,
        y_validation=y_validation,
    )

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    print()
    print("MurphAI Random Forest Model")
    print("=" * 40)

    print()
    print("Validation Metrics")
    print("-" * 40)

    print(
        f"ACCURACY  : {metrics['accuracy']:.4f}"
    )

    print(
        f"PRECISION : {metrics['precision']:.4f}"
    )

    print(
        f"RECALL    : {metrics['recall']:.4f}"
    )

    print(
        f"F1        : {metrics['f1']:.4f}"
    )

    print(
        f"ROC_AUC   : {metrics['roc_auc']:.4f}"
    )

    print()
    print("Model Configuration")
    print("-" * 40)

    print(
        f"Estimators          : {N_ESTIMATORS}"
    )

    print(
        f"Max depth           : {MAX_DEPTH}"
    )

    print(
        f"Min samples split   : {MIN_SAMPLES_SPLIT}"
    )

    print(
        f"Min samples leaf    : {MIN_SAMPLES_LEAF}"
    )

    print(
        f"Random state        : {RANDOM_STATE}"
    )


if __name__ == "__main__":
    main()