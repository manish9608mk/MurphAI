"""
Tests for MurphAI dataset splitting.
"""

import pandas as pd
import pytest

from ml.src.data.dataset_split import (
    RANDOM_STATE,
    TEST_SIZE,
    VALIDATION_SIZE,
    split_dataset,
)


# ============================================================
# Test Dataset
# ============================================================


def create_test_dataset():
    """Create a small balanced dataset for testing."""

    X = pd.DataFrame(
        {
            "feature_a": list(range(20)),
            "feature_b": list(range(100, 120)),
        }
    )

    y = pd.Series(
        [0, 1] * 10,
        name="successful",
    )

    return X, y


# ============================================================
# Basic Split Tests
# ============================================================


def test_split_dataset_sizes():
    """Verify train, validation, and test sizes."""

    X, y = create_test_dataset()

    (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    ) = split_dataset(X, y)

    assert len(X_train) == 12
    assert len(X_validation) == 4
    assert len(X_test) == 4

    assert len(y_train) == 12
    assert len(y_validation) == 4
    assert len(y_test) == 4


def test_split_dataset_preserves_features():
    """Verify all feature columns are preserved."""

    X, y = create_test_dataset()

    (
        X_train,
        X_validation,
        X_test,
        _,
        _,
        _,
    ) = split_dataset(X, y)

    assert list(X_train.columns) == list(X.columns)
    assert list(X_validation.columns) == list(X.columns)
    assert list(X_test.columns) == list(X.columns)


def test_split_dataset_preserves_total_rows():
    """Verify no rows are lost."""

    X, y = create_test_dataset()

    (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    ) = split_dataset(X, y)

    assert (
        len(X_train)
        + len(X_validation)
        + len(X_test)
        == len(X)
    )

    assert (
        len(y_train)
        + len(y_validation)
        + len(y_test)
        == len(y)
    )


def test_split_dataset_has_no_overlap():
    """Verify train, validation, and test sets do not overlap."""

    X, y = create_test_dataset()

    (
        X_train,
        X_validation,
        X_test,
        _,
        _,
        _,
    ) = split_dataset(X, y)

    train_indices = set(X_train.index)
    validation_indices = set(X_validation.index)
    test_indices = set(X_test.index)

    assert train_indices.isdisjoint(validation_indices)
    assert train_indices.isdisjoint(test_indices)
    assert validation_indices.isdisjoint(test_indices)


# ============================================================
# Target Distribution Tests
# ============================================================


def test_split_dataset_preserves_target_distribution():
    """Verify stratification preserves both target classes."""

    X, y = create_test_dataset()

    (
        _,
        _,
        _,
        y_train,
        y_validation,
        y_test,
    ) = split_dataset(X, y)

    assert set(y_train) == {0, 1}
    assert set(y_validation) == {0, 1}
    assert set(y_test) == {0, 1}


# ============================================================
# Reproducibility
# ============================================================


def test_split_is_reproducible():
    """Verify the same random state produces the same split."""

    X, y = create_test_dataset()

    first = split_dataset(X, y)
    second = split_dataset(X, y)

    for first_part, second_part in zip(first, second):
        pd.testing.assert_frame_equal(
            first_part,
            second_part,
        ) if isinstance(first_part, pd.DataFrame) else (
            pd.testing.assert_series_equal(
                first_part,
                second_part,
            )
        )


# ============================================================
# Validation Tests
# ============================================================


def test_mismatched_lengths_raise_error():
    """Verify X and y must have equal lengths."""

    X, y = create_test_dataset()

    y = y.iloc[:-1]

    with pytest.raises(
        ValueError,
        match="same number of rows",
    ):
        split_dataset(X, y)


def test_too_small_dataset_raises_error():
    """Verify very small datasets are rejected."""

    X = pd.DataFrame(
        {
            "feature_a": [1, 2, 3],
        }
    )

    y = pd.Series([0, 1, 0])

    with pytest.raises(
        ValueError,
        match="at least 10 rows",
    ):
        split_dataset(X, y)