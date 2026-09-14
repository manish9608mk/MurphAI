"""
MLflow tracking utilities for MurphAI.

This module provides the common MLflow configuration used by
model training, model registration, and model inference.

The tracking URI is environment-configurable so the same
application code can work with:

    - local SQLite during development
    - Docker-local MLflow storage
    - a remote MLflow Tracking Server in production

When a remote Tracking Server is used, artifact storage is
managed by that server instead of by the MurphAI application.
"""

import os
from pathlib import Path

import mlflow
import mlflow.sklearn


# MurphAI MLflow configuration

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Local MLflow metadata database.
#
# This is used only when MLFLOW_TRACKING_URI is not explicitly
# configured. Keeping the fallback local makes development easy
# while allowing production to provide its own Tracking Server.
MLFLOW_DB_PATH = Path(
    os.getenv(
        "MLFLOW_DB_PATH",
        str(PROJECT_ROOT / "mlflow.db"),
    )
)

# MLflow Tracking URI.
#
# Local default:
#     sqlite:///project/mlflow.db
#
# Production example:
#     http://mlflow.internal:5000
#
# An explicitly configured URI always takes precedence over
# the local SQLite fallback.
_configured_tracking_uri = os.getenv(
    "MLFLOW_TRACKING_URI",
    ""
).strip()

if _configured_tracking_uri:
    MLFLOW_TRACKING_URI = _configured_tracking_uri
else:
    MLFLOW_TRACKING_URI = (
        f"sqlite:///{MLFLOW_DB_PATH}"
    )

# Local artifact directory.
#
# This path is relevant only when MurphAI itself is using local
# SQLite tracking. With a remote Tracking Server, the server owns
# the artifact destination and this local directory is not used.
MLFLOW_ARTIFACT_ROOT = Path(
    os.getenv(
        "MLFLOW_ARTIFACT_ROOT",
        str(PROJECT_ROOT / "mlruns"),
    )
)

EXPERIMENT_NAME = "murphai-worker-job-matching"


def is_local_sqlite_tracking() -> bool:
    """
    Return whether MurphAI is using local SQLite tracking.

    This distinction is important because local artifact
    directories should only be created by the application
    when it is also responsible for local MLflow storage.
    """

    return MLFLOW_TRACKING_URI.startswith(
        "sqlite:///"
    )


def configure_mlflow() -> None:
    """
    Configure MLflow tracking and the MurphAI experiment.

    For local SQLite tracking, MurphAI creates the local database
    directory and artifact directory as needed.

    For a remote Tracking Server, MurphAI connects to the configured
    server and allows that server to control backend and artifact
    storage.
    """

    # Local filesystem preparation is required only when the
    # application itself owns the SQLite database and artifacts.
    if is_local_sqlite_tracking():
        MLFLOW_DB_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        MLFLOW_ARTIFACT_ROOT.mkdir(
            parents=True,
            exist_ok=True,
        )

    # Tell the MLflow client which tracking backend to use.
    mlflow.set_tracking_uri(
        MLFLOW_TRACKING_URI
    )

    experiment = mlflow.get_experiment_by_name(
        EXPERIMENT_NAME
    )

    if experiment is None:
        # A remote Tracking Server should control its own artifact
        # destination. Therefore artifact_location is provided only
        # for local SQLite tracking.
        if is_local_sqlite_tracking():
            mlflow.create_experiment(
                name=EXPERIMENT_NAME,
                artifact_location=str(
                    MLFLOW_ARTIFACT_ROOT
                ),
            )
        else:
            mlflow.create_experiment(
                name=EXPERIMENT_NAME,
            )

    mlflow.set_experiment(
        EXPERIMENT_NAME
    )


def start_run(run_name: str):
    """
    Start an MLflow run inside the MurphAI experiment.

    Training code does not need to know whether MLflow is running
    locally or behind a remote Tracking Server.
    """

    configure_mlflow()

    return mlflow.start_run(
        run_name=run_name
    )


def log_parameters(parameters: dict) -> None:
    """
    Log model parameters for the active MLflow run.

    Parameters
    ----------
    parameters : dict
        Model configuration values such as estimators,
        depth, and random seed.
    """

    mlflow.log_params(parameters)


def log_metrics(metrics: dict) -> None:
    """
    Log evaluation metrics for the active MLflow run.

    Parameters
    ----------
    metrics : dict
        Evaluation results such as accuracy, recall,
        F1 score, and ROC-AUC.
    """

    mlflow.log_metrics(metrics)


def log_model(
    model,
    artifact_path: str = "model",
) -> None:
    """
    Log a trained scikit-learn model to MLflow.

    Parameters
    ----------
    model :
        Trained scikit-learn model.

    artifact_path : str
        Logical artifact name used by model registration
        and later champion-model loading.
    """

    mlflow.sklearn.log_model(
        model,
        name=artifact_path,
    )