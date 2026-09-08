"""
FastAPI endpoints for MurphAI ML predictions.

This module exposes the worker-job matching
ML model through the REST API.
"""

from fastapi import APIRouter, Depends

from backend.app.core.security import get_current_user_id
from backend.app.schemas.ml import (
    WorkerJobPredictionRequest,
    WorkerJobPredictionResponse,
)
from backend.app.services.ml_service import (
    predict_worker_job_success,
)


router = APIRouter(
    prefix="/ml",
    tags=["ML"],
)


# ============================================================
# Worker-Job Success Prediction
# ============================================================


@router.post(
    "/predict",
    response_model=WorkerJobPredictionResponse,
)
def predict_worker_job(
    request: WorkerJobPredictionRequest,
    current_user_id: int = Depends(get_current_user_id),
) -> WorkerJobPredictionResponse:
    """
    Predict whether a worker-job interaction
    will be successful.

    Authentication is required because ML prediction
    is part of the MurphAI application.
    """

    return predict_worker_job_success(request)