"""
Feature preparation for MurphAI inference.

This module converts raw worker-job information
into the exact feature representation expected
by the trained champion model.

Training and inference must use the same feature logic.
"""

import pandas as pd


# ============================================================
# Expected Raw Features
# ============================================================

RAW_INFERENCE_COLUMNS = [
    "worker_experience_years",
    "worker_completed_jobs",
    "worker_success_rate",
    "worker_rating",
    "required_skill_count",
    "matched_skill_count",
    "location_match",
    "distance_km",
    "job_complexity",
    "job_budget",
]


# ============================================================
# Expected Engineered Features
# ============================================================

ENGINEERED_FEATURE_COLUMNS = [
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
# Feature Preparation
# ============================================================


def prepare_inference_features(
    data: dict,
) -> pd.DataFrame:
    """
    Convert raw worker-job data into ML-ready features.

    Parameters
    ----------
    data : dict
        Raw worker-job information.

    Returns
    -------
    pd.DataFrame
        Engineered features in the exact order
        expected by the champion model.

    Raises
    ------
    ValueError
        If required input fields are missing or invalid.
    """

    # --------------------------------------------------------
    # Step 1: Validate input type
    # --------------------------------------------------------

    if not isinstance(data, dict):
        raise TypeError(
            "Inference data must be a dictionary."
        )

    # --------------------------------------------------------
    # Step 2: Validate required raw fields
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in RAW_INFERENCE_COLUMNS
        if column not in data
    ]

    if missing_columns:
        raise ValueError(
            "Missing required inference fields: "
            f"{missing_columns}"
        )

    # --------------------------------------------------------
    # Step 3: Extract scalar input values
    # --------------------------------------------------------
    #
    # A single API request represents one worker-job pair.
    # Therefore these values are normal Python scalars,
    # not Pandas Series.
    #

    required_skill_count = data["required_skill_count"]
    matched_skill_count = data["matched_skill_count"]
    job_complexity = data["job_complexity"]

    # --------------------------------------------------------
    # Step 4: Validate skill counts
    # --------------------------------------------------------

    if required_skill_count <= 0:
        raise ValueError(
            "required_skill_count must be greater than zero."
        )

    if matched_skill_count < 0:
        raise ValueError(
            "matched_skill_count cannot be negative."
        )

    if matched_skill_count > required_skill_count:
        raise ValueError(
            "matched_skill_count cannot exceed "
            "required_skill_count."
        )

    # --------------------------------------------------------
    # Step 5: Validate job complexity
    # --------------------------------------------------------

    if job_complexity <= 0:
        raise ValueError(
            "job_complexity must be greater than zero."
        )

    # --------------------------------------------------------
    # Step 6: Create DataFrame
    # --------------------------------------------------------

    features = pd.DataFrame(
        [
            {
                column: data[column]
                for column in RAW_INFERENCE_COLUMNS
            }
        ]
    )

    # --------------------------------------------------------
    # Step 7: Calculate skill match ratio
    # --------------------------------------------------------

    features["skill_match_ratio"] = (
        features["matched_skill_count"]
        / features["required_skill_count"]
    )

    # --------------------------------------------------------
    # Step 8: Calculate skill gap
    # --------------------------------------------------------

    features["skill_gap"] = (
        features["required_skill_count"]
        - features["matched_skill_count"]
    )

    # --------------------------------------------------------
    # Step 9: Calculate worker reliability score
    # --------------------------------------------------------

    features["worker_reliability_score"] = (
        features["worker_success_rate"]
        * (
            features["worker_rating"]
            / 5.0
        )
    )

    # --------------------------------------------------------
    # Step 10: Calculate budget efficiency
    # --------------------------------------------------------

    features["budget_per_complexity"] = (
        features["job_budget"]
        / features["job_complexity"]
    )

    # --------------------------------------------------------
    # Step 11: Return exact model feature order
    # --------------------------------------------------------

    return features[
        ENGINEERED_FEATURE_COLUMNS
    ]