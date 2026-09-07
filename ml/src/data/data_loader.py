"""
Data Loading & Validation -
We'll create a proper data-loading layer:

CSV
 ↓
Data Loader
 ↓
Validation
 ↓
Clean DataFrame
 ↓
Feature Engineering

We'll use Pandas here.

Load and validate the MurphAI worker-job interaction dataset.

This module is responsible for:
    1. Locating the synthetic dataset.
    2. Loading the dataset into a Pandas DataFrame.
    3. Validating the dataset structure.
    4. Validating the target column.
    5. Returning a clean DataFrame for downstream ML work.
"""

from pathlib import Path

import pandas as pd


# ============================================================
# Dataset Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "synthetic"
    / "worker_job_interactions.csv"
)


REQUIRED_COLUMNS = {
    "worker_id",
    "job_id",
    "worker_experience_years",
    "worker_rating",
    "worker_completed_jobs",
    "worker_success_rate",
    "distance_km",
    "required_skill_count",
    "matched_skill_count",
    "skill_match_ratio",
    "job_budget",
    "job_complexity",
    "successful",
}


# ============================================================
# Data Loading
# ============================================================

def load_dataset(
    dataset_path: Path = DATASET_PATH,
) -> pd.DataFrame:
    """
    Load the MurphAI dataset from CSV.

    Args:
        dataset_path: Path to the dataset CSV file.

    Returns:
        Pandas DataFrame containing the dataset.

    Raises:
        FileNotFoundError:
            If the dataset does not exist.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}"
        )

    return pd.read_csv(dataset_path)


# ============================================================
# Data Validation
# ============================================================

def validate_dataset(
    df: pd.DataFrame,
) -> None:
    """
    Validate the structure and basic integrity of the dataset.

    Args:
        df: Dataset DataFrame.

    Raises:
        ValueError:
            If the dataset fails validation.
    """

    if df.empty:
        raise ValueError("Dataset is empty.")

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing_values = df[list(REQUIRED_COLUMNS)].isnull().sum()

    columns_with_missing_values = (
        missing_values[
            missing_values > 0
        ]
        .index
        .tolist()
    )

    if columns_with_missing_values:
        raise ValueError(
            "Missing values found in columns: "
            f"{columns_with_missing_values}"
        )

    # --------------------------------------------------------
    # Target validation
    # --------------------------------------------------------

    valid_target_values = {0, 1}

    actual_target_values = set(
        df["successful"].unique()
    )

    invalid_target_values = (
        actual_target_values - valid_target_values
    )

    if invalid_target_values:
        raise ValueError(
            "Invalid values found in target column "
            f"'successful': {sorted(invalid_target_values)}"
        )

    # --------------------------------------------------------
    # Numeric feature validation
    # --------------------------------------------------------

    numeric_columns = [
        "worker_experience_years",
        "worker_rating",
        "worker_completed_jobs",
        "worker_success_rate",
        "distance_km",
        "required_skill_count",
        "matched_skill_count",
        "skill_match_ratio",
        "job_budget",
        "job_complexity",
    ]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(
                f"Column '{column}' must contain numeric values."
            )


# ============================================================
# Public Dataset Interface
# ============================================================

def load_and_validate_dataset(
    dataset_path: Path = DATASET_PATH,
) -> pd.DataFrame:
    """
    Load and validate the MurphAI dataset.

    This is the main function that downstream ML
    components should use.

    Args:
        dataset_path: Path to the dataset CSV file.

    Returns:
        Validated Pandas DataFrame.
    """

    df = load_dataset(dataset_path)

    validate_dataset(df)

    return df