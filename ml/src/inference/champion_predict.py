"""
Champion model inference for MurphAI.

This module provides the production-facing inference layer
for the current champion model.

The champion model is resolved from the MLflow Model Registry
using the "champion" alias.

The loaded model is cached in application memory so MLflow
does not need to be contacted for every prediction request.

Responsibilities:
    1. Load and cache the champion model.
    2. Validate inference input.
    3. Generate a binary prediction.
    4. Generate success probability.
    5. Return a consistent prediction response.
"""

from functools import lru_cache

import mlflow
import mlflow.sklearn
import pandas as pd

from ml.src.features.feature_engineering import FEATURE_COLUMNS
from ml.src.registry.model_registry import (
    REGISTERED_MODEL_NAME,
    get_champion_model_uri,
)
from ml.src.tracking.mlflow_tracking import (
    MLFLOW_TRACKING_URI,
)


# Champion model configuration

CHAMPION_MODEL_NAME = "RandomForest"


# Champion model loading

@lru_cache(maxsize=1)
def load_champion_model():
    """
    Load the current champion model from MLflow and cache it.

    The champion model is resolved through the MLflow
    "champion" alias instead of using a hardcoded model version
    or local model file.

    The cache ensures that the model is normally loaded only
    once per application process. Subsequent predictions reuse
    the already loaded model from memory.

    A process restart automatically clears the cache.

    Returns
    -------
    object
        Loaded scikit-learn champion model.

    Raises
    ------
    Exception
        If the champion model cannot be loaded from MLflow.
    """

    # Configure MLflow before resolving the registered model.
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    # Build the model URI from the stable registered-model name
    # and the "champion" alias. This allows model promotion
    # without changing application code.
    model_uri = get_champion_model_uri(
        REGISTERED_MODEL_NAME
    )

    # Download/load the model from MLflow.
    #
    # Because this function is cached, this operation normally
    # happens only once per application process.
    return mlflow.sklearn.load_model(model_uri)


def clear_champion_model_cache() -> None:
    """
    Clear the in-memory champion model cache.

    This is useful when MurphAI promotes a new champion model
    and the running application needs to reload it.

    The function does not load a new model immediately.
    The next prediction will load the currently configured
    champion model from MLflow.
    """

    load_champion_model.cache_clear()


# Inference input validation

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


# Champion prediction

def predict_with_champion(
    features: pd.DataFrame,
) -> dict:
    """
    Generate a prediction using the cached champion model.

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

    # Step 1: Validate the incoming feature matrix.
    validate_features(features)

    # Step 2: Keep feature columns in exactly the same order
    # used during model training.
    model_features = features[FEATURE_COLUMNS].copy()

    # Step 3: Get the champion model.
    #
    # The first request loads the model from MLflow.
    # Later requests reuse the in-memory cached model.
    model = load_champion_model()

    # Step 4: Generate the binary prediction.
    prediction = model.predict(model_features)

    predicted_success = int(prediction[0])

    # Step 5: Generate the probability for the successful class.
    probabilities = model.predict_proba(
        model_features
    )

    success_probability = float(
        probabilities[0][1]
    )

    # Step 6: Return a stable response structure to the
    # backend service.
    return {
        "predicted_success": predicted_success,
        "success_probability": success_probability,
        "model_name": CHAMPION_MODEL_NAME,
    }


# Example features

def create_example_features() -> pd.DataFrame:
    """
    Create one example worker-job feature row.

    This function is only used by the command-line
    demonstration and local development checks.
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


# Command-line demonstration

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