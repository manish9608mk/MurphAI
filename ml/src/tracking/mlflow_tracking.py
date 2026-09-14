"""
MLflow tracking utilities for MurphAI.

This module provides the common MLflow configuration used by
model training, model registration, and model inference.

Storage is environment-configurable so the same application
can run on a developer machine, inside Docker, or in CI
without storing machine-specific filesystem paths.
"""

import os
from pathlib import Path

import mlflow
import mlflow.sklearn


# MurphAI MLflow storage configuration

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# The MLflow metadata database contains experiments, runs,
# registered models, versions, and aliases.
#
# Local development defaults to the project directory.
# Docker/production can override this with MLFLOW_DB_PATH.
MLFLOW_DB_PATH = Path(
    os.getenv(
        "MLFLOW_DB_PATH",
        str(PROJECT_ROOT / "mlflow.db"),
    )
)

MLFLOW_TRACKING_URI = (
    f"sqlite:///{MLFLOW_DB_PATH}"
)

# Model files logged by MLflow are stored under this directory.
#
# Local development defaults to project/mlruns.
# Docker can override this with /app/mlruns.
MLFLOW_ARTIFACT_ROOT = Path(
    os.getenv(
        "MLFLOW_ARTIFACT_ROOT",
        str(PROJECT_ROOT / "mlruns"),
    )
)

EXPERIMENT_NAME = "murphai-worker-job-matching"


def configure_mlflow() -> None:
    """
    Configure the MLflow tracking database and experiment.

    A new experiment is created with the configured artifact
    root when it does not already exist.

    Existing experiments keep the artifact location that was
    stored when they were created.
    """

    MLFLOW_DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    MLFLOW_ARTIFACT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    mlflow.set_tracking_uri(
        MLFLOW_TRACKING_URI
    )

    experiment = mlflow.get_experiment_by_name(
        EXPERIMENT_NAME
    )

    if experiment is None:
        mlflow.create_experiment(
            name=EXPERIMENT_NAME,
            artifact_location=str(
                MLFLOW_ARTIFACT_ROOT
            ),
        )

    mlflow.set_experiment(
        EXPERIMENT_NAME
    )


def start_run(run_name: str):
    """
    Start an MLflow run inside the MurphAI experiment.

    The experiment is configured before starting the run so
    training code does not need to know how MLflow storage
    is configured.
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