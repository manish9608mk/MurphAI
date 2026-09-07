from pathlib import Path

import mlflow
import pytest

from ml.src.tracking.mlflow_tracking import (
    EXPERIMENT_NAME,
    MLFLOW_TRACKING_URI,
    configure_mlflow,
    log_metrics,
    log_parameters,
    start_run,
)


def test_mlflow_tracking_uri():
    assert MLFLOW_TRACKING_URI.startswith("sqlite:///")


def test_configure_mlflow():
    configure_mlflow()

    experiment = mlflow.get_experiment_by_name(
        EXPERIMENT_NAME
    )

    assert experiment is not None
    assert experiment.name == EXPERIMENT_NAME


def test_start_run():
    with start_run("test-run") as run:
        assert run.info.run_id is not None
        assert run.info.run_name == "test-run"


def test_log_parameters():
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


def test_log_metrics():
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

        assert data.metrics["accuracy"] == pytest.approx(0.73)
        assert data.metrics["f1"] == pytest.approx(0.81)