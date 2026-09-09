"""
MLflow Model Registry utilities for MurphAI.

Responsibilities:
    1. Configure MLflow.
    2. Register a trained model from an MLflow run.
    3. Assign the champion alias.
    4. Retrieve the champion model version.
"""

import mlflow
from mlflow import MlflowClient

from ml.src.tracking.mlflow_tracking import (
    MLFLOW_TRACKING_URI,
)


# ============================================================
# Configuration
# ============================================================

REGISTERED_MODEL_NAME = "murphai-worker-job-matching"

CHAMPION_ALIAS = "champion"


# ============================================================
# MLflow Client
# ============================================================


def get_mlflow_client() -> MlflowClient:
    """
    Create an MLflow client connected to MurphAI's
    local tracking database.
    """

    mlflow.set_tracking_uri(
        MLFLOW_TRACKING_URI
    )

    return MlflowClient(
        tracking_uri=MLFLOW_TRACKING_URI
    )


# ============================================================
# Model Registration
# ============================================================


def register_model(
    run_id: str,
    model_name: str = REGISTERED_MODEL_NAME,
    artifact_name: str = "model",
):
    """
    Register a model from an existing MLflow run.

    Parameters
    ----------
    run_id : str
        MLflow run ID containing the logged model.

    model_name : str
        Registered model name.

    artifact_name : str
        Name of the logged MLflow model artifact.

    Returns
    -------
    ModelVersion
        Newly registered model version.
    """

    mlflow.set_tracking_uri(
        MLFLOW_TRACKING_URI
    )

    model_uri = (
        f"runs:/{run_id}/{artifact_name}"
    )

    model_version = mlflow.register_model(
        model_uri=model_uri,
        name=model_name,
    )

    return model_version


# ============================================================
# Champion Alias
# ============================================================


def set_champion_alias(
    model_name: str,
    version: str,
) -> None:
    """
    Assign the champion alias to a model version.
    """

    client = get_mlflow_client()

    client.set_registered_model_alias(
        model_name,
        CHAMPION_ALIAS,
        version,
    )


# ============================================================
# Champion Version
# ============================================================


def get_champion_version(
    model_name: str = REGISTERED_MODEL_NAME,
):
    """
    Retrieve the model version currently assigned
    to the champion alias.
    """

    client = get_mlflow_client()

    return client.get_model_version_by_alias(
        model_name,
        CHAMPION_ALIAS,
    )


# ============================================================
# Champion Model URI
# ============================================================


def get_champion_model_uri(
    model_name: str = REGISTERED_MODEL_NAME,
) -> str:
    """
    Return the MLflow URI for the champion model.
    """

    return (
        f"models:/{model_name}@{CHAMPION_ALIAS}"
    )


# ============================================================
# Find Latest Random Forest Run
# ============================================================


def get_latest_random_forest_run():
    """
    Find the most recent successful Random Forest training run.
    """

    client = get_mlflow_client()

    experiment = client.get_experiment_by_name(
        "murphai-worker-job-matching"
    )

    if experiment is None:
        raise ValueError(
            "MurphAI MLflow experiment not found."
        )

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=(
            "attributes.status = 'FINISHED' "
            "and attributes.run_name = 'random-forest-baseline'"
        ),
        order_by=["attributes.start_time DESC"],
        max_results=1,
    )

    if not runs:
        raise ValueError(
            "No completed Random Forest run found."
        )

    return runs[0]


# ============================================================
# Register Latest Random Forest
# ============================================================


def register_latest_random_forest():
    """
    Register the latest Random Forest training run
    and assign it as the champion model.
    """

    run = get_latest_random_forest_run()

    model_version = register_model(
        run_id=run.info.run_id,
    )

    set_champion_alias(
        model_name=REGISTERED_MODEL_NAME,
        version=model_version.version,
    )

    return model_version


# ============================================================
# Script Entry Point
# ============================================================


if __name__ == "__main__":
    model_version = register_latest_random_forest()

    print()
    print("MurphAI Model Registry")
    print("=" * 40)

    print(
        f"Model Name : {REGISTERED_MODEL_NAME}"
    )

    print(
        f"Version    : {model_version.version}"
    )

    print(
        f"Alias      : {CHAMPION_ALIAS}"
    )

    print(
        f"Source Run : {model_version.run_id}"
    )

    print()
    print(
        f"Champion URI: "
        f"{get_champion_model_uri()}"
    )