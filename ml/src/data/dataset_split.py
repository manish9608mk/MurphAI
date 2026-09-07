"""
Dataset splitting utilities for MurphAI.

This module separates the feature matrix and target into:

    Training set
    Validation set
    Test set

The split is performed before model training so that the
model is evaluated on data it has never seen during training.
"""

import pandas as pd

from sklearn.model_selection import train_test_split


# ============================================================
# Configuration
# ============================================================

TEST_SIZE = 0.20
VALIDATION_SIZE = 0.20
RANDOM_STATE = 42


# ============================================================
# Dataset Split
# ============================================================


def split_dataset(
    X: pd.DataFrame,
    y: pd.Series,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
    pd.Series,
]:
    """
    Split features and target into train, validation, and test sets.

    The final proportions are:

        60% training
        20% validation
        20% test

    Parameters
    ----------
    X : pd.DataFrame
        ML feature matrix.

    y : pd.Series
        Target variable.

    Returns
    -------
    X_train : pd.DataFrame
    X_validation : pd.DataFrame
    X_test : pd.DataFrame
    y_train : pd.Series
    y_validation : pd.Series
    y_test : pd.Series
    """

    if len(X) != len(y):
        raise ValueError(
            "X and y must contain the same number of rows."
        )

    if len(X) < 10:
        raise ValueError(
            "Dataset must contain at least 10 rows."
        )

    # --------------------------------------------------------
    # First split:
    #
    # 80% temporary training data
    # 20% final test data
    # --------------------------------------------------------

    X_temp, X_test, y_temp, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # --------------------------------------------------------
    # Second split:
    #
    # From the remaining 80%:
    #
    # 75% -> training
    # 25% -> validation
    #
    # Therefore:
    #
    # 80% × 75% = 60% training
    # 80% × 25% = 20% validation
    # 20% = test
    # --------------------------------------------------------

    validation_ratio_of_temp = (
        VALIDATION_SIZE / (1 - TEST_SIZE)
    )

    X_train, X_validation, y_train, y_validation = (
        train_test_split(
            X_temp,
            y_temp,
            test_size=validation_ratio_of_temp,
            random_state=RANDOM_STATE,
            stratify=y_temp,
        )
    )

    return (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    )