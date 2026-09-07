"""
Tests for MurphAI feature engineering.
"""

import pandas as pd
import pytest

from ml.src.features.feature_engineering import (
    FEATURE_COLUMNS,
    RAW_FEATURE_COLUMNS,
    TARGET_COLUMN,
    create_features,
    prepare_features,
)


# ============================================================
# Test Dataset
# ============================================================


def create_test_dataframe():
    """Create a small dataset for testing."""

    return pd.DataFrame(
        [
            {
                "worker_id": 1,
                "job_id": 101,
                "worker_experience_years": 5,
                "worker_completed_jobs": 50,
                "worker_success_rate": 0.80,
                "worker_rating": 4.5,
                "required_skill_count": 4,
                "matched_skill_count": 3,
                "skill_match_ratio": 0.75,
                "location_match": 1,
                "distance_km": 5.0,
                "job_complexity": 4,
                "job_budget": 10000.0,
                "successful": 1,
            },
            {
                "worker_id": 2,
                "job_id": 101,
                "worker_experience_years": 2,
                "worker_completed_jobs": 15,
                "worker_success_rate": 0.60,
                "worker_rating": 3.5,
                "required_skill_count": 4,
                "matched_skill_count": 1,
                "skill_match_ratio": 0.25,
                "location_match": 0,
                "distance_km": 35.0,
                "job_complexity": 4,
                "job_budget": 10000.0,
                "successful": 0,
            },
        ]
    )


# ============================================================
# Feature Creation Tests
# ============================================================


def test_create_features_returns_expected_columns():
    """Verify final feature columns are correct."""

    df = create_test_dataframe()

    features = create_features(df)

    assert list(features.columns) == FEATURE_COLUMNS


def test_create_features_preserves_row_count():
    """Verify feature engineering does not change row count."""

    df = create_test_dataframe()

    features = create_features(df)

    assert len(features) == len(df)


def test_identifiers_are_removed():
    """Verify worker_id and job_id are not ML features."""

    df = create_test_dataframe()

    features = create_features(df)

    assert "worker_id" not in features.columns
    assert "job_id" not in features.columns


def test_target_is_not_in_features():
    """Verify target is not included in X."""

    df = create_test_dataframe()

    features = create_features(df)

    assert TARGET_COLUMN not in features.columns


# ============================================================
# Derived Feature Tests
# ============================================================


def test_skill_gap():
    """Verify skill gap calculation."""

    df = create_test_dataframe()

    features = create_features(df)

    assert features.loc[0, "skill_gap"] == 1
    assert features.loc[1, "skill_gap"] == 3


def test_worker_reliability_score():
    """Verify worker reliability score calculation."""

    df = create_test_dataframe()

    features = create_features(df)

    expected_first = 0.80 * (4.5 / 5.0)

    assert abs(
        features.loc[0, "worker_reliability_score"]
        - expected_first
    ) < 0.0001


def test_budget_per_complexity():
    """Verify budget per complexity calculation."""

    df = create_test_dataframe()

    features = create_features(df)

    assert features.loc[0, "budget_per_complexity"] == 2500.0
    assert features.loc[1, "budget_per_complexity"] == 2500.0


# ============================================================
# X and y Preparation Tests
# ============================================================


def test_prepare_features():
    """Verify X and y are separated correctly."""

    df = create_test_dataframe()

    X, y = prepare_features(df)

    assert isinstance(X, pd.DataFrame)
    assert isinstance(y, pd.Series)

    assert len(X) == 2
    assert len(y) == 2

    assert list(X.columns) == FEATURE_COLUMNS

    assert y.tolist() == [1, 0]


# ============================================================
# Missing Column Tests
# ============================================================


def test_missing_column_raises_error():
    """Verify missing required columns are rejected."""

    df = create_test_dataframe()

    df = df.drop(columns=["worker_rating"])

    with pytest.raises(ValueError, match="Missing required columns"):
        create_features(df)