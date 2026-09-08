"""
Tests for MurphAI inference feature preparation.
"""

import pytest

from ml.src.features.inference_features import (
    ENGINEERED_FEATURE_COLUMNS,
    prepare_inference_features,
)


# ============================================================
# Test Data
# ============================================================


def valid_input() -> dict:
    return {
        "worker_experience_years": 5,
        "worker_completed_jobs": 30,
        "worker_success_rate": 0.90,
        "worker_rating": 4.7,
        "required_skill_count": 3,
        "matched_skill_count": 3,
        "location_match": 1,
        "distance_km": 5.0,
        "job_complexity": 2,
        "job_budget": 5000.0,
    }


# ============================================================
# Tests
# ============================================================


def test_prepare_inference_features_returns_dataframe():
    result = prepare_inference_features(
        valid_input()
    )

    assert not result.empty
    assert len(result) == 1


def test_engineered_features_have_expected_columns():
    result = prepare_inference_features(
        valid_input()
    )

    assert list(result.columns) == ENGINEERED_FEATURE_COLUMNS


def test_skill_match_ratio_is_calculated():
    result = prepare_inference_features(
        valid_input()
    )

    assert result.loc[0, "skill_match_ratio"] == pytest.approx(1.0)


def test_skill_gap_is_calculated():
    result = prepare_inference_features(
        valid_input()
    )

    assert result.loc[0, "skill_gap"] == 0


def test_worker_reliability_score_is_calculated():
    result = prepare_inference_features(
        valid_input()
    )

    expected = 0.90 * (4.7 / 5.0)

    assert result.loc[0, "worker_reliability_score"] == pytest.approx(
        expected
    )


def test_budget_per_complexity_is_calculated():
    result = prepare_inference_features(
        valid_input()
    )

    assert result.loc[0, "budget_per_complexity"] == pytest.approx(
        2500.0
    )


def test_missing_required_field_is_rejected():
    data = valid_input()

    del data["worker_rating"]

    with pytest.raises(ValueError, match="Missing required inference fields"):
        prepare_inference_features(data)


def test_matched_skills_cannot_exceed_required_skills():
    data = valid_input()

    data["matched_skill_count"] = 4

    with pytest.raises(
        ValueError,
        match="matched_skill_count cannot exceed",
    ):
        prepare_inference_features(data)


def test_zero_required_skills_are_rejected():
    data = valid_input()

    data["required_skill_count"] = 0

    with pytest.raises(
        ValueError,
        match="required_skill_count must be greater than zero",
    ):
        prepare_inference_features(data)


def test_zero_job_complexity_is_rejected():
    data = valid_input()

    data["job_complexity"] = 0

    with pytest.raises(
        ValueError,
        match="job_complexity must be greater than zero",
    ):
        prepare_inference_features(data)