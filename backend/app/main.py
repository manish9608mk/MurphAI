import logging

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.dependencies import get_db
from backend.app.core.exception_handlers import (
    assignment_already_exists_exception_handler,
    assignment_not_found_exception_handler,
    email_already_registered_handler,
    invalid_assignment_transition_handler,
    invalid_job_status_transition_handler,
    invalid_job_interest_transition_handler,
    job_interest_already_exists_exception_handler,
    job_interest_not_found_exception_handler,
    job_not_found_handler,
    permission_denied_handler,
    unexpected_exception_handler,
    user_not_found_handler,
    worker_already_exists_exception_handler,
    worker_not_found_exception_handler,
    worker_skill_already_exists_handler,
    worker_skill_not_found_handler,
    worker_unavailable_exception_handler,
)
from backend.app.core.exceptions import (
    AssignmentAlreadyExistsException,
    AssignmentNotFoundException,
    EmailAlreadyRegisteredException,
    InvalidAssignmentTransitionException,
    InvalidJobStatusTransitionException,
    InvalidJobInterestTransitionException,
    JobInterestAlreadyExistsException,
    JobInterestNotFoundException,
    JobNotFoundException,
    PermissionDeniedException,
    UserNotFoundException,
    WorkerAlreadyExistsException,
    WorkerNotFoundException,
    WorkerSkillAlreadyExistsException,
    WorkerSkillNotFoundException,
    WorkerUnavailableException,
)
from backend.app.core.logging import configure_logging
from backend.app.core.middleware import RequestLoggingMiddleware

# API routers
from backend.app.api.assignments import router as assignments_router
from backend.app.api.auth import router as auth_router
from backend.app.api.confirmation import router as confirmation_router
from backend.app.api.evidence import router as evidence_router
from backend.app.api.job_interests import (
    router as job_interests_router,
    job_router as job_interests_job_router,
)
from backend.app.api.jobs import router as jobs_router
from backend.app.api.ml import router as ml_router
from backend.app.api.payment import router as payment_router
from backend.app.api.reputation import router as reputation_router
from backend.app.api.skills import router as skills_router
from backend.app.api.users import router as users_router
from backend.app.api.work import router as work_router
from backend.app.api.workers import router as workers_router


# FastAPI Application

app = FastAPI(
    title=settings.app_name,
    description="AI-powered intelligent system",
    version=settings.app_version,
)

configure_logging()

logger = logging.getLogger(__name__)

# Request Observability
app.add_middleware(
    RequestLoggingMiddleware,
)


# CORS

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
        ],
        allow_headers=[
            "Authorization",
            "Content-Type",
        ],
    )


# EXCEPTION HANDLERS

app.add_exception_handler(
    UserNotFoundException,
    user_not_found_handler,
)

app.add_exception_handler(
    EmailAlreadyRegisteredException,
    email_already_registered_handler,
)

app.add_exception_handler(
    JobNotFoundException,
    job_not_found_handler,
)

app.add_exception_handler(
    InvalidJobStatusTransitionException,
    invalid_job_status_transition_handler,
)

app.add_exception_handler(
    WorkerNotFoundException,
    worker_not_found_exception_handler,
)

app.add_exception_handler(
    WorkerAlreadyExistsException,
    worker_already_exists_exception_handler,
)

app.add_exception_handler(
    WorkerSkillAlreadyExistsException,
    worker_skill_already_exists_handler,
)

app.add_exception_handler(
    WorkerSkillNotFoundException,
    worker_skill_not_found_handler,
)

app.add_exception_handler(
    AssignmentNotFoundException,
    assignment_not_found_exception_handler,
)

app.add_exception_handler(
    AssignmentAlreadyExistsException,
    assignment_already_exists_exception_handler,
)

app.add_exception_handler(
    InvalidAssignmentTransitionException,
    invalid_assignment_transition_handler,
)

app.add_exception_handler(
    WorkerUnavailableException,
    worker_unavailable_exception_handler,
)

app.add_exception_handler(
    JobInterestNotFoundException,
    job_interest_not_found_exception_handler,
)

app.add_exception_handler(
    JobInterestAlreadyExistsException,
    job_interest_already_exists_exception_handler,
)

app.add_exception_handler(
    InvalidJobInterestTransitionException,
    invalid_job_interest_transition_handler,
)

app.add_exception_handler(
    PermissionDeniedException,
    permission_denied_handler,
)

app.add_exception_handler(
    Exception,
    unexpected_exception_handler,
)


# API Routers

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(workers_router)
app.include_router(skills_router)
app.include_router(assignments_router)
app.include_router(job_interests_router)
app.include_router(job_interests_job_router)
app.include_router(work_router)
app.include_router(evidence_router)
app.include_router(confirmation_router)
app.include_router(payment_router)
app.include_router(reputation_router)
app.include_router(ml_router)


# Liveness Endpoint

@app.get("/health")
def health():
    """
    Confirm that the API process is alive.
    """

    return {
        "status": "healthy",
        "service": settings.app_name,
    }


# Readiness Endpoint

@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    """
    Confirm that the API can reach the application database.
    """

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "service": settings.app_name,
            "database": "ready",
        }

    except SQLAlchemyError:
        db.rollback()

        logger.exception(
            "Database readiness check failed",
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready",
        )


# Root Endpoint

@app.get("/")
def root():
    """
    Basic application endpoint.
    """

    logger.info("MurphAI root endpoint called")

    return {
        "message": f"{settings.app_name} is running",
    }
