"""
Generate synthetic historical worker-job interactions for MurphAI.

The generated dataset is designed for the first MurphAI ML problem:

    Worker ↔ Job Matching

Each row represents one worker considered for one job.

The target column is:

    successful
        1 = successful outcome
        0 = unsuccessful outcome

The features are based only on information that could be known
before the worker performs the job, helping us avoid data leakage.
"""

import csv
import math
import random
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

RANDOM_SEED = 42

NUMBER_OF_WORKERS = 200
NUMBER_OF_JOBS = 300
CANDIDATES_PER_JOB = 15

OUTPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "synthetic"
    / "worker_job_interactions.csv"
)


# ============================================================
# Domain Configuration
# ============================================================

SKILLS = [
    "electrical",
    "wiring",
    "plumbing",
    "painting",
    "carpentry",
    "hvac",
    "appliance_repair",
    "construction",
    "masonry",
    "welding",
]

LOCATIONS = [
    "Bhopal",
    "Indore",
    "Delhi",
    "Mumbai",
    "Pune",
    "Bengaluru",
    "Hyderabad",
    "Jaipur",
    "Patna",
    "Lucknow",
]


# ============================================================
# Helper Functions
# ============================================================


def sigmoid(value: float) -> float:
    """Convert a score into a probability between 0 and 1."""

    return 1.0 / (1.0 + math.exp(-value))


def choose_unique_items(
    rng: random.Random,
    items: list[str],
    minimum: int,
    maximum: int,
) -> list[str]:
    """Choose a random number of unique items from a list."""

    count = rng.randint(minimum, maximum)

    return rng.sample(items, count)


# ============================================================
# Synthetic Worker Generation
# ============================================================


def generate_workers(
    rng: random.Random,
) -> list[dict]:
    """
    Generate synthetic worker profiles.

    Historical worker statistics represent information available
    before a new job is considered.
    """

    workers = []

    for worker_id in range(1, NUMBER_OF_WORKERS + 1):

        # Years of professional experience.
        experience_years = rng.randint(0, 15)

        # Historical number of completed jobs.
        completed_jobs = rng.randint(
            max(1, experience_years),
            max(5, experience_years * 8 + 5),
        )

        # Generate a realistic historical success rate.
        base_success_rate = 0.55 + min(
            experience_years * 0.025,
            0.30,
        )

        success_rate = min(
            0.98,
            max(
                0.50,
                base_success_rate + rng.uniform(-0.10, 0.08),
            ),
        )

        # Rating is correlated with historical success rate.
        rating = min(
            5.0,
            max(
                2.5,
                3.0
                + success_rate * 1.8
                + rng.uniform(-0.35, 0.25),
            ),
        )

        worker = {
            "worker_id": worker_id,
            "experience_years": experience_years,
            "completed_jobs": completed_jobs,
            "success_rate": round(success_rate, 4),
            "rating": round(rating, 2),
            "location": rng.choice(LOCATIONS),
            "skills": choose_unique_items(
                rng,
                SKILLS,
                minimum=1,
                maximum=4,
            ),
        }

        workers.append(worker)

    return workers


# ============================================================
# Synthetic Job Generation
# ============================================================


def generate_jobs(
    rng: random.Random,
) -> list[dict]:
    """
    Generate synthetic jobs.

    Job complexity is deliberately generated as a pre-job feature.
    """

    jobs = []

    for job_id in range(1, NUMBER_OF_JOBS + 1):

        required_skills = choose_unique_items(
            rng,
            SKILLS,
            minimum=1,
            maximum=3,
        )

        job = {
            "job_id": job_id,
            "required_skills": required_skills,
            "location": rng.choice(LOCATIONS),
            "budget": round(
                rng.uniform(500.0, 15000.0),
                2,
            ),
            "complexity": rng.randint(1, 5),
        }

        jobs.append(job)

    return jobs


# ============================================================
# Feature Calculation
# ============================================================


def calculate_skill_features(
    worker: dict,
    job: dict,
) -> tuple[int, int, float]:
    """
    Calculate worker-job skill compatibility.

    Returns:

        required_skill_count
        matched_skill_count
        skill_match_ratio
    """

    required_skills = set(job["required_skills"])
    worker_skills = set(worker["skills"])

    matched_skills = required_skills.intersection(
        worker_skills
    )

    required_skill_count = len(required_skills)
    matched_skill_count = len(matched_skills)

    skill_match_ratio = (
        matched_skill_count / required_skill_count
        if required_skill_count > 0
        else 0.0
    )

    return (
        required_skill_count,
        matched_skill_count,
        round(skill_match_ratio, 4),
    )


# ============================================================
# Distance Feature
# ============================================================


def generate_distance_km(
    rng: random.Random,
    location_match: int,
) -> float:
    """
    Generate an approximate distance between worker and job.

    A location match produces a shorter distance on average.
    """

    if location_match:
        return round(
            rng.uniform(0.5, 10.0),
            2,
        )

    return round(
        rng.uniform(10.0, 50.0),
        2,
    )


# ============================================================
# Outcome Generation
# ============================================================


def generate_successful_outcome(
    rng: random.Random,
    worker: dict,
    skill_match_ratio: float,
    location_match: int,
    job_complexity: int,
) -> int:
    """
    Generate a synthetic job outcome.

    The probability of success depends on:

        - skill compatibility
        - worker experience
        - historical success rate
        - historical reputation
        - location compatibility
        - job complexity

    These are all pre-job features.
    """

    experience_score = min(
        worker["experience_years"] / 10.0,
        1.0,
    )

    rating_score = (
        worker["rating"] / 5.0
    )

    complexity_score = (
        job_complexity / 5.0
    )

    # Higher complexity should reduce the chance of success.
    complexity_penalty = 1.2 * complexity_score

    score = (
        -2.0
        + 2.8 * skill_match_ratio
        + 1.0 * experience_score
        + 2.0 * worker["success_rate"]
        + 0.8 * rating_score
        + 0.7 * location_match
        - complexity_penalty
    )

    probability = sigmoid(score)

    return int(
        rng.random() < probability
    )


# ============================================================
# Dataset Generation
# ============================================================


def generate_dataset(
    rng: random.Random,
) -> list[dict]:
    """Generate worker-job interaction records."""

    workers = generate_workers(rng)
    jobs = generate_jobs(rng)

    rows = []

    for job in jobs:

        candidate_workers = rng.sample(
            workers,
            min(
                CANDIDATES_PER_JOB,
                len(workers),
            ),
        )

        for worker in candidate_workers:

            (
                required_skill_count,
                matched_skill_count,
                skill_match_ratio,
            ) = calculate_skill_features(
                worker,
                job,
            )

            location_match = int(
                worker["location"] == job["location"]
            )

            distance_km = generate_distance_km(
                rng,
                location_match,
            )

            successful = generate_successful_outcome(
                rng,
                worker,
                skill_match_ratio,
                location_match,
                job["complexity"],
            )

            rows.append(
                {
                    "worker_id": worker["worker_id"],
                    "job_id": job["job_id"],
                    "worker_experience_years": worker[
                        "experience_years"
                    ],
                    "worker_completed_jobs": worker[
                        "completed_jobs"
                    ],
                    "worker_success_rate": worker[
                        "success_rate"
                    ],
                    "worker_rating": worker[
                        "rating"
                    ],
                    "required_skill_count": required_skill_count,
                    "matched_skill_count": matched_skill_count,
                    "skill_match_ratio": skill_match_ratio,
                    "location_match": location_match,
                    "distance_km": distance_km,
                    "job_complexity": job[
                        "complexity"
                    ],
                    "job_budget": job[
                        "budget"
                    ],
                    "successful": successful,
                }
            )

    return rows


# ============================================================
# CSV Writing
# ============================================================


def save_dataset(
    rows: list[dict],
    output_path: Path,
) -> None:
    """Save generated dataset as a CSV file."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not rows:
        raise ValueError(
            "Cannot save an empty dataset."
        )

    fieldnames = list(
        rows[0].keys()
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# Main
# ============================================================


def main() -> None:
    """Generate and save the synthetic MurphAI dataset."""

    rng = random.Random(
        RANDOM_SEED
    )

    rows = generate_dataset(rng)

    save_dataset(
        rows,
        OUTPUT_PATH,
    )

    successful_count = sum(
        row["successful"]
        for row in rows
    )

    success_rate = (
        successful_count / len(rows)
    )

    print(
        "Synthetic MurphAI dataset "
        "generated successfully."
    )

    print(
        f"Rows: {len(rows)}"
    )

    print(
        f"Successful outcomes: "
        f"{successful_count}"
    )

    print(
        f"Unsuccessful outcomes: "
        f"{len(rows) - successful_count}"
    )

    print(
        f"Overall success rate: "
        f"{success_rate:.2%}"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()