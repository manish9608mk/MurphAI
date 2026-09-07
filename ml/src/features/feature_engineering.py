"""
Feature engineering for MurphAI worker-job matching.

This module converts raw worker-job data into the
feature representation expected by the ML models.

Two preparation paths are supported:

    1. Training / evaluation
       Raw dataset -> X + y

    2. Inference
       Single prediction input -> X

The feature engineering logic is shared between
training and inference to prevent feature mismatch.
"""

import pandas as pd


# ============================================================
# Raw Input Columns
# ============================================================

RAW_FEATURE_COLUMNS = [
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
]


TARGET_COLUMN = "successful"


# ============================================================
# Final ML Feature Columns
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
# Feature Engineering
# ============================================================


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the final feature set used by the ML model.

    Parameters
    ----------
    df : pd.DataFrame
        Raw worker-job interaction data.

    Returns
    -------
    pd.DataFrame
        DataFrame containing only ML features.
    """

    # --------------------------------------------------------
    # Validate required feature columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in RAW_FEATURE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # --------------------------------------------------------
    # Copy raw features
    # --------------------------------------------------------

    features = df[RAW_FEATURE_COLUMNS].copy()

    # --------------------------------------------------------
    # Derived Feature 1: Skill Gap
    # --------------------------------------------------------

    # Number of required skills the worker does not match.

    features["skill_gap"] = (
        features["required_skill_count"]
        - features["matched_skill_count"]
    )

    # --------------------------------------------------------
    # Derived Feature 2: Worker Reliability Score
    # --------------------------------------------------------

    # Combines:
    #
    #   historical success rate
    #   worker rating
    #
    # Rating is normalized from 1-5 to 0.2-1.0.

    features["worker_reliability_score"] = (
        features["worker_success_rate"]
        * (features["worker_rating"] / 5.0)
    )

    # --------------------------------------------------------
    # Derived Feature 3: Budget per Complexity
    # --------------------------------------------------------

    # Represents how much budget is available
    # relative to job difficulty.

    features["budget_per_complexity"] = (
        features["job_budget"]
        / features["job_complexity"]
    )

    # --------------------------------------------------------
    # Return final model features
    # --------------------------------------------------------

    return features[FEATURE_COLUMNS]


# ============================================================
# Training / Evaluation Preparation
# ============================================================


def prepare_features(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Prepare features and target for training or evaluation.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset containing features and target.

    Returns
    -------
    tuple[pd.DataFrame, pd.Series]
        X and y.
    """

    # --------------------------------------------------------
    # Validate target
    # --------------------------------------------------------

    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Missing required target column: {TARGET_COLUMN}"
        )

    # --------------------------------------------------------
    # Create model features
    # --------------------------------------------------------

    X = create_features(df)

    # --------------------------------------------------------
    # Extract target
    # --------------------------------------------------------

    y = df[TARGET_COLUMN].copy()

    return X, y


# ============================================================
# Inference Preparation
# ============================================================


def prepare_inference_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare features for model inference.

    Unlike prepare_features(), this function does not
    require the target column because the target is exactly
    what the model is predicting.

    Parameters
    ----------
    df : pd.DataFrame
        Raw worker-job input.

    Returns
    -------
    pd.DataFrame
        Feature matrix ready for model prediction.
    """

    return create_features(df)