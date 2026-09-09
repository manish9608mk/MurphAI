import mlflow

from ml.src.registry.model_registry import (
    CHAMPION_ALIAS,
    REGISTERED_MODEL_NAME,
    get_champion_model_uri,
    get_mlflow_client,
)


def test_registered_model_name():
    assert (
        REGISTERED_MODEL_NAME
        == "murphai-worker-job-matching"
    )


def test_champion_alias():
    assert CHAMPION_ALIAS == "champion"


def test_get_mlflow_client():
    client = get_mlflow_client()

    assert client is not None


def test_get_champion_model_uri():
    uri = get_champion_model_uri()

    assert (
        uri
        == "models:/murphai-worker-job-matching@champion"
    )