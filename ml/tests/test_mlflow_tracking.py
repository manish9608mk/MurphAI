"""
Tests for MurphAI MLflow tracking.

These tests verify:

    1. Local SQLite tracking configuration.
    2. MLflow experiment creation.
    3. Local artifact storage configuration.
    4. MLflow run creation.
    5. Parameter logging.
    6. Metric logging.
    7. Model artifact logging.
    8. Remote Tracking Server detection.
    9. Remote Tracking Server configuration behavior.
"""

import mlflow
import pytest
from sklearn.linear_model import LogisticRegression

import ml.src.tracking.mlflow_tracking as mlflow_tracking


# MLflow test configuration

@pytest.fixture(autouse=True)
def isolated_mlflow(tmp_path, monkeypatch):
    """
    Give every test its own local MLflow database and artifact
    directory so tests cannot modify real development data.

    The fixture also resets MLflow's active run after every test
    to prevent state from leaking between tests.
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


# Local MLflow configuration

def test_mlflow_tracking_uri():
    """
    Verify that the isolated test environment uses
    SQLite for local MLflow tracking.
    """

    assert mlflow_tracking.MLFLOW_TRACKING_URI.startswith(
        "sqlite:///"
    )


def test_configure_mlflow():
    """
    Verify that the MurphAI MLflow experiment is created
    and can be retrieved successfully.
    """

    mlflow_tracking.configure_mlflow()

    experiment = mlflow.get_experiment_by_name(
        mlflow_tracking.EXPERIMENT_NAME
    )

    assert experiment is not None
    assert experiment.name == (
        mlflow_tracking.EXPERIMENT_NAME
    )


def test_mlflow_artifact_location():
    """
    Verify that local MLflow artifacts are stored under
    the configured artifact root.
    """

    mlflow_tracking.configure_mlflow()

    experiment = mlflow.get_experiment_by_name(
        mlflow_tracking.EXPERIMENT_NAME
    )

    assert experiment is not None

    expected_root = (
        mlflow_tracking.MLFLOW_ARTIFACT_ROOT
    )

    assert experiment.artifact_location == str(
        expected_root
    )


# MLflow runs

def test_start_run():
    """
    Verify that MurphAI can start a named MLflow run.
    """

    with mlflow_tracking.start_run("test-run") as run:

        assert run.info.run_id is not None
        assert run.info.run_name == "test-run"


def test_log_parameters():
    """
    Verify that model parameters are recorded correctly
    in an MLflow run.
    """

    with mlflow_tracking.start_run(
        "parameter-test"
    ):

        mlflow_tracking.log_parameters(
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

    with mlflow_tracking.start_run(
        "metric-test"
    ):

        mlflow_tracking.log_metrics(
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

    with mlflow_tracking.start_run(
        "model-test"
    ):

        mlflow_tracking.log_model(
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


# Remote MLflow configuration

def test_remote_tracking_uri_is_detected(monkeypatch):
    """
    Verify that the MLflow configuration correctly
    identifies a remote Tracking Server URI.

    This test changes only the configuration value; it does
    not require a real remote MLflow server to be running.
    """

    remote_tracking_uri = (
        "http://mlflow.internal:5000"
    )

    monkeypatch.setattr(
        mlflow_tracking,
        "MLFLOW_TRACKING_URI",
        remote_tracking_uri,
    )

    assert (
        mlflow_tracking.is_local_sqlite_tracking()
        is False
    )


def test_remote_tracking_does_not_create_local_storage(
    monkeypatch,
    tmp_path,
):
    """
    Verify that remote MLflow configuration does not create
    local SQLite or artifact directories.

    When a remote Tracking Server is configured, its server-side
    storage is responsible for the backend database and artifacts.
    """

    remote_tracking_uri = (
        "http://mlflow.internal:5000"
    )

    local_db_path = (
        tmp_path / "should_not_be_created" / "mlflow.db"
    )

    local_artifact_root = (
        tmp_path / "should_not_be_created" / "mlruns"
    )

    monkeypatch.setattr(
        mlflow_tracking,
        "MLFLOW_TRACKING_URI",
        remote_tracking_uri,
    )

    monkeypatch.setattr(
        mlflow_tracking,
        "MLFLOW_DB_PATH",
        local_db_path,
    )

    monkeypatch.setattr(
        mlflow_tracking,
        "MLFLOW_ARTIFACT_ROOT",
        local_artifact_root,
    )

    # Simulate the remote MLflow server being reachable.
    #
    # These mocks allow us to test MurphAI's configuration logic
    # without requiring an actual production Tracking Server.
    monkeypatch.setattr(
        mlflow,
        "set_tracking_uri",
        lambda uri: None,
    )

    monkeypatch.setattr(
        mlflow,
        "get_experiment_by_name",
        lambda name: None,
    )

    created_experiments = []

    def fake_create_experiment(
        name,
        **kwargs,
    ):
        """
        Record how the experiment is created.

        A remote configuration must not force a local
        artifact_location.
        """

        created_experiments.append(
            {
                "name": name,
                "kwargs": kwargs,
            }
        )

        return "remote-experiment-id"

    monkeypatch.setattr(
        mlflow,
        "create_experiment",
        fake_create_experiment,
    )

    monkeypatch.setattr(
        mlflow,
        "set_experiment",
        lambda name: None,
    )

    mlflow_tracking.configure_mlflow()

    assert not local_db_path.exists()
    assert not local_artifact_root.exists()

    assert len(created_experiments) == 1

    created_experiment = (
        created_experiments[0]
    )

    assert created_experiment["name"] == (
        mlflow_tracking.EXPERIMENT_NAME
    )

    # MurphAI should allow the remote MLflow server to
    # determine the artifact destination.
    assert "artifact_location" not in (
        created_experiment["kwargs"]
    )