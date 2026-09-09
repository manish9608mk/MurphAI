"""
Champion model inference for MurphAI.

This module provides the production-facing inference layer
for the current champion model.

The champion model is loaded from the MLflow Model Registry
using the "champion" alias.

Responsibilities:
    1. Load the champion model from MLflow.
    2. Validate inference input.
    3. Generate a binary prediction.
    4. Generate success probability.
    5. Return a consistent prediction response.
"""

import pandas as pd
import mlflow.sklearn

from ml.src.features.feature_engineering import FEATURE_COLUMNS
from ml.src.registry.model_registry import (
    REGISTERED_MODEL_NAME,
    CHAMPION_ALIAS,
    get_champion_model_uri,
)
from ml.src.tracking.mlflow_tracking import (
    MLFLOW_TRACKING_URI,
)


# ============================================================
# Configuration
# ============================================================

CHAMPION_MODEL_NAME = "RandomForest"


# ============================================================
# Model Loading
# ============================================================


def load_champion_model():
    """
    Load the current champion model from MLflow Model Registry.

    The model is resolved using the "champion" alias rather
    than a hardcoded local model file.

    Returns
    -------
    object
        Loaded scikit-learn champion model.

    Raises
    ------
    Exception
        If the champion model cannot be loaded from MLflow.
    """

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    model_uri = get_champion_model_uri(
        REGISTERED_MODEL_NAME
    )

    return mlflow.sklearn.load_model(model_uri)


# ============================================================
# Input Validation
# ============================================================


def validate_features(
    features: pd.DataFrame,
) -> None:
    """
    Validate feature input before inference.

    Parameters
    ----------
    features : pd.DataFrame
        Feature matrix for prediction.

    Raises
    ------
    TypeError
        If input is not a DataFrame.

    ValueError
        If input is empty or missing required features.
    """

    if not isinstance(features, pd.DataFrame):
        raise TypeError(
            "features must be a pandas DataFrame."
        )

    if features.empty:
        raise ValueError(
            "Features cannot be empty."
        )

    missing_columns = [
        column
        for column in FEATURE_COLUMNS
        if column not in features.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required feature columns: "
            f"{missing_columns}"
        )


# ============================================================
# Champion Prediction
# ============================================================


def predict_with_champion(
    features: pd.DataFrame,
) -> dict:
    """
    Generate a prediction using the current champion model.

    Parameters
    ----------
    features : pd.DataFrame
        Feature matrix containing the exact features
        used during model training.

    Returns
    -------
    dict
        Prediction result containing:

            predicted_success
            success_probability
            model_name
    """

    # --------------------------------------------------------
    # Step 1: Validate input
    # --------------------------------------------------------

    validate_features(features)

    # --------------------------------------------------------
    # Step 2: Keep features in training order
    # --------------------------------------------------------

    model_features = features[FEATURE_COLUMNS].copy()

    # --------------------------------------------------------
    # Step 3: Load champion model from MLflow Registry
    # --------------------------------------------------------

    model = load_champion_model()

    # --------------------------------------------------------
    # Step 4: Generate prediction
    # --------------------------------------------------------

    prediction = model.predict(model_features)

    predicted_success = int(prediction[0])

    # --------------------------------------------------------
    # Step 5: Generate probability
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        model_features
    )

    success_probability = float(
        probabilities[0][1]
    )

    # --------------------------------------------------------
    # Step 6: Return standardized result
    # --------------------------------------------------------

    return {
        "predicted_success": predicted_success,
        "success_probability": success_probability,
        "model_name": CHAMPION_MODEL_NAME,
    }


# ============================================================
# Example Features
# ============================================================


def create_example_features() -> pd.DataFrame:
    """
    Create one example worker-job feature row.

    This is only used for the command-line demonstration.
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
                "skill_gap": 0,
                "worker_reliability_score": 0.846,
                "budget_per_complexity": 2500.0,
            }
        ]
    )


# ============================================================
# CLI
# ============================================================


def main() -> None:
    """
    Run a sample champion prediction.
    """

    features = create_example_features()

    result = predict_with_champion(features)

    print()
    print("MurphAI Champion Model Prediction")
    print("=" * 45)

    print(
        f"Model                 : {result['model_name']}"
    )

    print(
        f"Prediction            : "
        f"{'successful' if result['predicted_success'] == 1 else 'unsuccessful'}"
    )

    print(
        f"Successful            : "
        f"{result['predicted_success']}"
    )

    print(
        f"Success Probability   : "
        f"{result['success_probability']:.4f}"
    )

    print(
        f"Success Probability   : "
        f"{result['success_probability']:.2%}"
    )


if __name__ == "__main__":
    main()