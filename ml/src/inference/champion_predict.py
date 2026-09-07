"""
Champion model inference for MurphAI.

This module provides the production-facing inference layer
for the current champion model.

Current champion:
    RandomForest

Responsibilities:
    1. Load the champion model.
    2. Validate inference input.
    3. Generate a binary prediction.
    4. Generate success probability.
    5. Return a consistent prediction response.
"""

from pathlib import Path

import pandas as pd


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "worker_job_random_forest.joblib"
)


CHAMPION_MODEL_NAME = "RandomForest"


# ============================================================
# Expected Features
# ============================================================

FEATURE_COLUMNS = [
    "worker_experience_years",
    "worker_completed_jobs",
    "worker_success_rate",
    "worker_rating",
    "required_skill_count",
    "matched_skill_count",
    "skill_match_ratio",
    "location_match",
    "distance_km",
    "job_complexity",
    "job_budget",
    "skill_gap",
    "worker_reliability_score",
    "budget_per_complexity",
]


# ============================================================
# Model Loading
# ============================================================


def load_champion_model(
    model_path: Path = MODEL_PATH,
):
    """
    Load the current champion model from disk.

    Parameters
    ----------
    model_path : Path
        Location of the saved champion model.

    Returns
    -------
    object
        Loaded Random Forest model.

    Raises
    ------
    FileNotFoundError
        If the model file does not exist.
    """

    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Champion model not found: {model_path}"
        )

    # Import joblib only when the model is loaded.
    import joblib

    return joblib.load(model_path)


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
    # Step 3: Load champion model
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
# Example CLI
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
                "worker_reliability_score": 0.90,
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