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
        If required input fields are missing.
    """

    # --------------------------------------------------------
    # Step 1: Validate required raw fields
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
    # Step 2: Create DataFrame
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
    # Step 3: Calculate skill match ratio
    # --------------------------------------------------------

    required_skill_count = features[
        "required_skill_count"
    ]

    matched_skill_count = features[
        "matched_skill_count"
    ]

    if (required_skill_count <= 0).any():
        raise ValueError(
            "required_skill_count must be greater than zero."
        )

    if (
        matched_skill_count
        > required_skill_count
    ).any():
        raise ValueError(
            "matched_skill_count cannot exceed "
            "required_skill_count."
        )

    features["skill_match_ratio"] = (
        matched_skill_count
        / required_skill_count
    )

    # --------------------------------------------------------
    # Step 4: Calculate skill gap
    # --------------------------------------------------------

    features["skill_gap"] = (
        required_skill_count
        - matched_skill_count
    )

    # --------------------------------------------------------
    # Step 5: Calculate worker reliability score
    # --------------------------------------------------------

    features["worker_reliability_score"] = (
        features["worker_success_rate"]
        * (
            features["worker_rating"]
            / 5.0
        )
    )

    # --------------------------------------------------------
    # Step 6: Calculate budget efficiency
    # --------------------------------------------------------

    job_complexity = features[
        "job_complexity"
    ]

    if (job_complexity <= 0).any():
        raise ValueError(
            "job_complexity must be greater than zero."
        )

    features["budget_per_complexity"] = (
        features["job_budget"]
        / job_complexity
    )

    # --------------------------------------------------------
    # Step 7: Return exact model feature order
    # --------------------------------------------------------

    return features[
        ENGINEERED_FEATURE_COLUMNS
    ]