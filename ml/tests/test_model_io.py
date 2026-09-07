"""
Tests for MurphAI model persistence.
"""

from pathlib import Path

import pytest
from sklearn.linear_model import LogisticRegression

from ml.src.models.model_io import (
    save_model,
    load_model,
)


def test_save_model_creates_file(tmp_path):
    model = LogisticRegression()

    model_path = tmp_path / "test_model.joblib"

    saved_path = save_model(
        model,
        model_path,
    )

    assert saved_path == model_path
    assert model_path.exists()


def test_load_model_returns_model(tmp_path):
    model = LogisticRegression()

    model_path = tmp_path / "test_model.joblib"

    save_model(
        model,
        model_path,
    )

    loaded_model = load_model(
        model_path,
    )

    assert isinstance(
        loaded_model,
        LogisticRegression,
    )


def test_load_model_missing_file_raises_error(tmp_path):
    model_path = tmp_path / "missing_model.joblib"

    with pytest.raises(FileNotFoundError):
        load_model(model_path)


def test_saved_model_can_make_predictions(tmp_path):
    model = LogisticRegression()

    X = [
        [1, 2],
        [2, 3],
        [3, 4],
        [4, 5],
    ]

    y = [0, 0, 1, 1]

    model.fit(X, y)

    model_path = tmp_path / "test_model.joblib"

    save_model(
        model,
        model_path,
    )

    loaded_model = load_model(
        model_path,
    )

    predictions = loaded_model.predict(X)

    assert len(predictions) == len(X)