"""
MLflow tracking utilities for MurphAI.

Responsibilities:
    1. Configure the MLflow experiment.
    2. Start an MLflow run.
    3. Log model parameters.
    4. Log evaluation metrics.
    5. Log the trained model.
"""

from pathlib import Path

import mlflow
import mlflow.sklearn


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MLFLOW_DB_PATH = PROJECT_ROOT / "mlflow.db"

MLFLOW_TRACKING_URI = f"sqlite:///{MLFLOW_DB_PATH}"

EXPERIMENT_NAME = "murphai-worker-job-matching"


def configure_mlflow() -> None:
    """
    Configure the local MLflow tracking database.
    """

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    mlflow.set_experiment(EXPERIMENT_NAME)


def start_run(run_name: str):
    """
    Start an MLflow experiment run.

    Returns:
        Active MLflow run context.
    """

    configure_mlflow()

    return mlflow.start_run(
        run_name=run_name
    )


def log_parameters(parameters: dict) -> None:
    """
    Log model parameters to the active MLflow run.
    """

    mlflow.log_params(parameters)


def log_metrics(metrics: dict) -> None:
    """
    Log evaluation metrics to the active MLflow run.
    """

    mlflow.log_metrics(metrics)


def log_model(model, artifact_path: str = "model") -> None:
    """
    Log a scikit-learn model to MLflow.
    """

    mlflow.sklearn.log_model(
        model,
        artifact_path=artifact_path,
    )