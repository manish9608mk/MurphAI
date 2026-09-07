"""
Model persistence utilities for MurphAI.

This module is responsible for saving and loading
trained machine learning models.
"""

from pathlib import Path

import joblib


# ============================================================
# Model Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIRECTORY = PROJECT_ROOT / "models"

MODEL_PATH = MODEL_DIRECTORY / "worker_job_baseline.joblib"


# ============================================================
# Save Model
# ============================================================


def save_model(
    model,
    model_path: Path = MODEL_PATH,
) -> Path:
    """
    Save a trained ML model to disk.

    Parameters
    ----------
    model :
        Trained scikit-learn model.

    model_path : Path
        Location where the model should be saved.

    Returns
    -------
    Path
        Path of the saved model.
    """

    model_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        model_path,
    )

    return model_path


# ============================================================
# Load Model
# ============================================================


def load_model(
    model_path: str | Path = MODEL_PATH,
):
    """
    Load a trained ML model from disk.

    Parameters
    ----------
    model_path : str | Path
        Location of the saved model.

    Returns
    -------
    object
        Loaded ML model.

    Raises
    ------
    FileNotFoundError
        If the model file does not exist.
    """

    # Convert string paths to Path objects.
    model_path = Path(model_path)

    # Make sure the model exists.
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    # Load and return the trained model.
    return joblib.load(model_path)