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


# MLflow test configuration

@pytest.fixture(autouse=True)
def isolated_mlflow(tmp_path, monkeypatch):
    """
    Give every test its own MLflow database and artifact
    directory so tests cannot modify real development data.
    """

    test_db_path = tmp_path / "mlflow_test.db"
    test_artifact_root = tmp_path / "mlruns"

    test_tracking_uri = (
        f"sqlite:///{test_db_path}"
    )

    monkeypatch.setattr(
        mlflow_tracking,
        "MLFLOW_TRACKING_URI",
        test_tracking_uri,
    )

    monkeypatch.setattr(
        mlflow_tracking,
        "MLFLOW_DB_PATH",
        test_db_path,
    )

    monkeypatch.setattr(
        mlflow_tracking,
        "MLFLOW_ARTIFACT_ROOT",
        test_artifact_root,
    )

    mlflow.set_tracking_uri(
        test_tracking_uri
    )

    yield

    if mlflow.active_run() is not None:
        mlflow.end_run()


def test_mlflow_tracking_uri():
    """
    Verify that MurphAI uses SQLite for local MLflow tracking.
    """

    assert MLFLOW_TRACKING_URI.startswith(
        "sqlite:///"
    )


def test_configure_mlflow():
    """
    Verify that the MurphAI MLflow experiment is created
    and can be retrieved successfully.
    """

    configure_mlflow()

    experiment = mlflow.get_experiment_by_name(
        EXPERIMENT_NAME
    )

    assert experiment is not None
    assert experiment.name == EXPERIMENT_NAME


def test_mlflow_artifact_location():
    """
    Verify that MLflow stores artifacts under the configured
    artifact root for the current environment.
    """

    configure_mlflow()

    experiment = mlflow.get_experiment_by_name(
        EXPERIMENT_NAME
    )

    assert experiment is not None

    expected_root = (
        mlflow_tracking.MLFLOW_ARTIFACT_ROOT
    )

    assert experiment.artifact_location == str(
        expected_root
    )


def test_start_run():
    """
    Verify that MurphAI can start a named MLflow run.
    """

    with start_run("test-run") as run:

        assert run.info.run_id is not None
        assert run.info.run_name == "test-run"


def test_log_parameters():
    """
    Verify that model parameters are recorded correctly
    in an MLflow run.
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


def test_log_metrics():
    """
    Verify that evaluation metrics are recorded correctly
    in an MLflow run.
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


def test_log_model():
    """
    Verify that a scikit-learn model can be logged as an
    MLflow model artifact.
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