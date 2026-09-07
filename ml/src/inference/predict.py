"""
MurphAI inference pipeline.

This module loads the trained worker-job matching model
and generates predictions for new worker-job interactions.
"""

from pathlib import Path

import joblib
import pandas as pd

from ml.src.features.feature_engineering import create_features


# ============================================================
# Model Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "worker_job_baseline.joblib"
)


# ============================================================
# Model Loading
# ============================================================


def load_model(model_path: Path = MODEL_PATH):
    """
    Load the trained ML model from disk.

    Parameters
    ----------
    model_path : Path
        Location of the saved model.

    Returns
    -------
    object
        Loaded scikit-learn model.

    Raises
    ------
    FileNotFoundError
        If the model file does not exist.
    """

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    return joblib.load(model_path)


# ============================================================
# Prediction
# ============================================================


def predict_success(
    interaction: dict,
    model=None,
) -> dict:
    """
    Predict the probability that a worker-job interaction
    will be successful.

    Parameters
    ----------
    interaction : dict
        Raw worker-job interaction data.

    model : optional
        Already-loaded ML model.

    Returns
    -------
    dict
        Prediction result containing:

            success_probability
            predicted_success
    """

    if model is None:
        model = load_model()

    # Convert the single interaction into a DataFrame.
    df = pd.DataFrame([interaction])

    # Create the exact same features used during training.
    features = create_features(
        df.assign(successful=0)
    )

    # Get probability for class 1 (successful).
    success_probability = model.predict_proba(
        features
    )[0][1]

    predicted_success = int(
        model.predict(features)[0]
    )

    return {
        "success_probability": float(success_probability),
        "predicted_success": predicted_success,
    }


# ============================================================
# Example Usage
# ============================================================


if __name__ == "__main__":

    example_interaction = {
        "worker_experience_years": 5,
        "worker_completed_jobs": 42,
        "worker_success_rate": 0.88,
        "worker_rating": 4.6,
        "required_skill_count": 5,
        "matched_skill_count": 4,
        "skill_match_ratio": 0.8,
        "location_match": 1,
        "distance_km": 3.5,
        "job_complexity": 3,
        "job_budget": 2500,
    }

    result = predict_success(
        example_interaction
    )

    print("MurphAI Worker-Job Prediction")
    print("=" * 40)
    print(
        f"Success Probability: "
        f"{result['success_probability']:.4f}"
    )
    print(
        f"Predicted Success: "
        f"{result['predicted_success']}"
    )