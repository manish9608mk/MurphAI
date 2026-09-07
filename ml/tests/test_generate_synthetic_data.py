"""
Tests for MurphAI synthetic worker-job dataset generation.
"""

import csv
import random

from ml.src.data.generate_synthetic_data import (
    RANDOM_SEED,
    NUMBER_OF_JOBS,
    CANDIDATES_PER_JOB,
    NUMBER_OF_WORKERS,
    calculate_skill_features,
    choose_unique_items,
    generate_dataset,
    generate_jobs,
    generate_successful_outcome,
    generate_workers,
    save_dataset,
    sigmoid,
)


# ============================================================
# Expected Dataset Schema
# ============================================================

EXPECTED_COLUMNS = {
    "worker_id",
    "job_id",
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
    "successful",
}


# ============================================================
# Helper Tests
# ============================================================


def test_sigmoid():
    """Verify sigmoid produces valid probability values."""

    assert sigmoid(0) == 0.5
    assert 0 < sigmoid(-10) < 0.5
    assert 0.5 < sigmoid(10) < 1


def test_choose_unique_items():
    """Verify unique item selection."""

    rng = random.Random(
        RANDOM_SEED
    )

    items = [
        "a",
        "b",
        "c",
        "d",
        "e",
    ]

    selected = choose_unique_items(
        rng,
        items,
        minimum=2,
        maximum=3,
    )

    assert 2 <= len(selected) <= 3
    assert len(set(selected)) == len(selected)

    assert all(
        item in items
        for item in selected
    )


def test_choose_unique_items_returns_all_when_count_matches():
    """Verify selecting the full collection."""

    rng = random.Random(
        RANDOM_SEED
    )

    items = [
        "a",
        "b",
        "c",
    ]

    selected = choose_unique_items(
        rng,
        items,
        minimum=3,
        maximum=3,
    )

    assert len(selected) == 3
    assert set(selected) == set(items)


# ============================================================
# Worker Generation Tests
# ============================================================


def test_generate_workers():
    """Verify worker generation."""

    rng = random.Random(
        RANDOM_SEED
    )

    workers = generate_workers(
        rng
    )

    assert len(workers) == (
        NUMBER_OF_WORKERS
    )

    worker_ids = {
        worker["worker_id"]
        for worker in workers
    }

    assert len(worker_ids) == (
        NUMBER_OF_WORKERS
    )

    for worker in workers:

        assert worker["worker_id"] > 0

        assert (
            worker["experience_years"]
            >= 0
        )

        assert (
            worker["completed_jobs"]
            >= 0
        )

        assert (
            0
            <= worker["success_rate"]
            <= 1
        )

        assert (
            1
            <= worker["rating"]
            <= 5
        )

        assert worker["location"]

        assert len(worker["skills"]) >= 1

        assert len(worker["skills"]) <= 4


# ============================================================
# Job Generation Tests
# ============================================================


def test_generate_jobs():
    """Verify job generation."""

    rng = random.Random(
        RANDOM_SEED
    )

    jobs = generate_jobs(
        rng
    )

    assert len(jobs) == (
        NUMBER_OF_JOBS
    )

    job_ids = {
        job["job_id"]
        for job in jobs
    }

    assert len(job_ids) == (
        NUMBER_OF_JOBS
    )

    for job in jobs:

        assert job["job_id"] > 0

        assert (
            len(job["required_skills"])
            >= 1
        )

        assert (
            len(job["required_skills"])
            <= 3
        )

        assert job["budget"] > 0

        assert (
            1
            <= job["complexity"]
            <= 5
        )

        assert job["location"]


# ============================================================
# Skill Feature Tests
# ============================================================


def test_calculate_skill_features():
    """Verify skill matching calculations."""

    worker = {
        "skills": [
            "electrical",
            "wiring",
            "maintenance",
        ],
    }

    job = {
        "required_skills": [
            "electrical",
            "wiring",
            "plumbing",
        ],
    }

    (
        required_skill_count,
        matched_skill_count,
        skill_match_ratio,
    ) = calculate_skill_features(
        worker,
        job,
    )

    assert required_skill_count == 3
    assert matched_skill_count == 2
    assert abs(skill_match_ratio - (2 / 3)) < 0.0001


def test_calculate_skill_features_with_no_match():
    """Verify skill matching when there is no overlap."""

    worker = {
        "skills": [
            "electrical",
        ],
    }

    job = {
        "required_skills": [
            "plumbing",
            "painting",
        ],
    }

    (
        required_skill_count,
        matched_skill_count,
        skill_match_ratio,
    ) = calculate_skill_features(
        worker,
        job,
    )

    assert required_skill_count == 2
    assert matched_skill_count == 0
    assert skill_match_ratio == 0


# ============================================================
# Outcome Tests
# ============================================================


def test_generate_successful_outcome_is_binary():
    """Verify generated outcome is always 0 or 1."""

    rng = random.Random(
        RANDOM_SEED
    )

    worker = {
        "experience_years": 5,
        "success_rate": 0.80,
        "rating": 4.2,
    }

    outcomes = [
        generate_successful_outcome(
            rng,
            worker,
            skill_match_ratio=0.8,
            location_match=1,
            job_complexity=3,
        )
        for _ in range(100)
    ]

    assert all(
        outcome in {0, 1}
        for outcome in outcomes
    )


def test_generate_successful_outcome_is_deterministic_with_same_seed():
    """Verify the same seed produces the same outcomes."""

    worker = {
        "experience_years": 5,
        "success_rate": 0.80,
        "rating": 4.2,
    }

    rng_one = random.Random(
        RANDOM_SEED
    )

    rng_two = random.Random(
        RANDOM_SEED
    )

    outcomes_one = [
        generate_successful_outcome(
            rng_one,
            worker,
            skill_match_ratio=0.8,
            location_match=1,
            job_complexity=3,
        )
        for _ in range(20)
    ]

    outcomes_two = [
        generate_successful_outcome(
            rng_two,
            worker,
            skill_match_ratio=0.8,
            location_match=1,
            job_complexity=3,
        )
        for _ in range(20)
    ]

    assert outcomes_one == outcomes_two


# ============================================================
# Dataset Tests
# ============================================================


def test_generate_dataset():
    """Verify the complete dataset has the expected structure."""

    rng = random.Random(
        RANDOM_SEED
    )

    rows = generate_dataset(
        rng
    )

    expected_rows = (
        NUMBER_OF_JOBS
        * CANDIDATES_PER_JOB
    )

    assert len(rows) == (
        expected_rows
    )

    assert set(
        rows[0].keys()
    ) == EXPECTED_COLUMNS


def test_dataset_feature_ranges():
    """Verify all generated ML features contain valid values."""

    rng = random.Random(
        RANDOM_SEED
    )

    rows = generate_dataset(
        rng
    )

    for row in rows:

        assert row["worker_id"] > 0
        assert row["job_id"] > 0

        assert (
            row["worker_experience_years"]
            >= 0
        )

        assert (
            row["worker_completed_jobs"]
            >= 0
        )

        assert (
            0
            <= row["worker_success_rate"]
            <= 1
        )

        assert (
            1
            <= row["worker_rating"]
            <= 5
        )

        assert (
            row["required_skill_count"]
            > 0
        )

        assert (
            0
            <= row["matched_skill_count"]
            <= row["required_skill_count"]
        )

        assert (
            0
            <= row["skill_match_ratio"]
            <= 1
        )

        assert row["location_match"] in {
            0,
            1,
        }

        assert (
            row["distance_km"]
            >= 0
        )

        assert (
            1
            <= row["job_complexity"]
            <= 5
        )

        assert (
            row["job_budget"]
            > 0
        )

        assert row["successful"] in {
            0,
            1,
        }


# ============================================================
# Dataset Consistency Tests
# ============================================================


def test_skill_match_ratio_is_consistent():
    """Verify skill ratio matches skill counts."""

    rng = random.Random(
        RANDOM_SEED
    )

    rows = generate_dataset(
        rng
    )

    for row in rows:

        expected_ratio = (
            row["matched_skill_count"]
            / row["required_skill_count"]
        )

        assert abs(
            row["skill_match_ratio"]
            - expected_ratio
        ) < 0.0001


def test_location_and_distance_are_consistent():
    """
    Verify location matching produces sensible
    distance values.
    """

    rng = random.Random(
        RANDOM_SEED
    )

    rows = generate_dataset(
        rng
    )

    for row in rows:

        if row["location_match"] == 1:
            assert (
                0.5
                <= row["distance_km"]
                <= 10.0
            )

        else:
            assert (
                10.0
                <= row["distance_km"]
                <= 50.0
            )


# ============================================================
# CSV Saving Tests
# ============================================================


def test_save_dataset(tmp_path):
    """Verify dataset is correctly written to CSV."""

    rng = random.Random(
        RANDOM_SEED
    )

    rows = generate_dataset(
        rng
    )

    output_path = (
        tmp_path
        / "test_dataset.csv"
    )

    save_dataset(
        rows,
        output_path,
    )

    assert output_path.exists()

    with output_path.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(
            file
        )

        saved_rows = list(
            reader
        )

    assert len(saved_rows) == len(
        rows
    )

    assert set(
        saved_rows[0].keys()
    ) == EXPECTED_COLUMNS