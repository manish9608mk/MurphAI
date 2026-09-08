"""
Schemas for MurphAI ML prediction APIs.

These schemas define the contract between the API
and the worker-job matching ML system.
"""

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# ML Prediction Request
# ============================================================


class WorkerJobPredictionRequest(BaseModel):
    """
    Input data required to predict the success
    of a worker-job interaction.

    The client provides raw business-level features.
    Derived ML features are calculated internally.
    """

    worker_experience_years: int = Field(
        ge=0,
        description="Worker's total experience in years.",
    )

    worker_completed_jobs: int = Field(
        ge=0,
        description="Number of jobs completed by the worker.",
    )

    worker_success_rate: float = Field(
        ge=0.0,
        le=1.0,
        description="Historical worker success rate.",
    )

    worker_rating: float = Field(
        ge=0.0,
        le=5.0,
        description="Worker's average customer rating.",
    )

    required_skill_count: int = Field(
        ge=1,
        description="Number of skills required by the job.",
    )

    matched_skill_count: int = Field(
        ge=0,
        description="Number of required skills matched by the worker.",
    )

    location_match: int = Field(
        ge=0,
        le=1,
        description="Whether the worker location matches the job location.",
    )

    distance_km: float = Field(
        ge=0.0,
        description="Distance between worker and job location in kilometers.",
    )

    job_complexity: int = Field(
        ge=1,
        description="Complexity level of the job.",
    )

    job_budget: float = Field(
        gt=0.0,
        description="Budget available for the job.",
    )

    model_config = ConfigDict(
        extra="forbid",
    )


# ============================================================
# ML Prediction Response
# ============================================================


class WorkerJobPredictionResponse(BaseModel):
    """
    Prediction returned by the MurphAI ML system.
    """

    predicted_success: int = Field(
        ge=0,
        le=1,
        description="Binary prediction: 1 for successful, 0 for unsuccessful.",
    )

    success_probability: float = Field(
        ge=0.0,
        le=1.0,
        description="Probability that the worker-job interaction will succeed.",
    )

    model_name: str = Field(
        min_length=1,
        description="Name of the ML model used for prediction.",
    )

    model_config = ConfigDict(
        from_attributes=True,
    )