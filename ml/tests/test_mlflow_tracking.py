import mlflow
import pytest
from sklearn.linear_model import LogisticRegression

import ml.src.tracking.mlflow_tracking as mlflow_tracking

from ml.src.tracking.mlflow_tracking import (
    EXPERIMENT_NAME,
    MLFLOW_TRACKING_URI,
    configure_mlflow,
    log_metrics,
    log_model,
    log_parameters,
    start_run,
)


# ============================================================
# Test Configuration
# ============================================================


@pytest.fixture(autouse=True)
def isolated_mlflow(tmp_path, monkeypatch):
    """
    Use a temporary MLflow database for every test.

    This prevents tests from modifying the real
    project mlflow.db database.
    """

    test_db_path = tmp_path / "mlflow_test.db"

    test_tracking_uri = (
        f"sqlite:///{test_db_path}"
    )

    monkeypatch.setattr(
        mlflow_tracking,
        "MLFLOW_TRACKING_URI",
        test_tracking_uri,
    )

    mlflow.set_tracking_uri(
        test_tracking_uri
    )

    yield

    # Make sure no active run remains after a test.
    if mlflow.active_run() is not None:
        mlflow.end_run()


# ============================================================
# Tracking URI
# ============================================================


def test_mlflow_tracking_uri():
    """
    Verify that the production tracking URI
    uses SQLite.
    """

    assert MLFLOW_TRACKING_URI.startswith(
        "sqlite:///"
    )


# ============================================================
# MLflow Configuration
# ============================================================


def test_configure_mlflow():
    """
    Verify that MurphAI's MLflow experiment
    can be configured successfully.
    """

    configure_mlflow()

    experiment = mlflow.get_experiment_by_name(
        EXPERIMENT_NAME
    )

    assert experiment is not None
    assert experiment.name == EXPERIMENT_NAME


# ============================================================
# Run Management
# ============================================================


def test_start_run():
    """
    Verify that an MLflow run can be started.
    """

    with start_run("test-run") as run:

        assert run.info.run_id is not None
        assert run.info.run_name == "test-run"


# ============================================================
# Parameter Logging
# ============================================================


def test_log_parameters():
    """
    Verify that model parameters are logged
    correctly.
    """

    with start_run("parameter-test"):

        log_parameters(
            {
                "model_type": "RandomForest",
                "n_estimators": 200,
            }
        )

        run = mlflow.active_run()

        assert run is not None

        client = mlflow.MlflowClient()

        data = client.get_run(
            run.info.run_id
        ).data

        assert data.params["model_type"] == "RandomForest"
        assert data.params["n_estimators"] == "200"


# ============================================================
# Metric Logging
# ============================================================


def test_log_metrics():
    """
    Verify that evaluation metrics are logged
    correctly.
    """

    with start_run("metric-test"):

        log_metrics(
            {
                "accuracy": 0.73,
                "f1": 0.81,
            }
        )

        run = mlflow.active_run()

        assert run is not None

        client = mlflow.MlflowClient()

        data = client.get_run(
            run.info.run_id
        ).data

        assert data.metrics["accuracy"] == pytest.approx(
            0.73
        )

        assert data.metrics["f1"] == pytest.approx(
            0.81
        )


# ============================================================
# Model Logging
# ============================================================


def test_log_model():
    """
    Verify that a scikit-learn model can be
    logged to MLflow.
    """

    model = LogisticRegression()

    model.fit(
        [[0], [1], [2], [3]],
        [0, 0, 1, 1],
    )

    with start_run("model-test"):

        log_model(
            model,
            artifact_path="model",
        )

        run = mlflow.active_run()

        assert run is not None

        client = mlflow.MlflowClient()

        run_data = client.get_run(
            run.info.run_id
        )

        assert run_data.info.run_id is not None