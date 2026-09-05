from fastapi import FastAPI

from backend.app.core.config import settings

# ============================================================
# API Routers
# ============================================================

# API routers
from backend.app.api.users import router as users_router
from backend.app.api.auth import router as auth_router
from backend.app.api.jobs import router as jobs_router
from backend.app.api.workers import router as workers_router
from backend.app.api.skills import router as skills_router
from backend.app.api.assignments import router as assignments_router
from backend.app.api.work import router as work_router
from backend.app.api.evidence import router as evidence_router
from backend.app.api.confirmation import router as confirmation_router
from backend.app.api.payment import router as payment_router
from backend.app.api.reputation import router as reputation_router


# ============================================================
# Custom Exceptions
# ============================================================

from backend.app.core.exceptions import (
    UserNotFoundException,
    EmailAlreadyRegisteredException,

    JobNotFoundException,
    InvalidJobStatusTransitionException,

    WorkerNotFoundException,
    WorkerAlreadyExistsException,

    WorkerSkillAlreadyExistsException,
    WorkerSkillNotFoundException,

    AssignmentNotFoundException,
    AssignmentAlreadyExistsException,
    InvalidAssignmentTransitionException,
    WorkerUnavailableException,

    PermissionDeniedException,
)


# ============================================================
# Exception Handlers
# ============================================================

from backend.app.core.exception_handlers import (
    user_not_found_handler,
    email_already_registered_handler,

    job_not_found_handler,
    invalid_job_status_transition_handler,

    worker_not_found_exception_handler,
    worker_already_exists_exception_handler,

    worker_skill_already_exists_handler,
    worker_skill_not_found_handler,

    assignment_not_found_exception_handler,
    assignment_already_exists_exception_handler,
    invalid_assignment_transition_handler,
    worker_unavailable_exception_handler,

    permission_denied_handler,
)


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="MurphAI",
    description="AI-powered intelligent system",
    version="0.1.0",
)


# ============================================================
# Exception Handlers
# ============================================================

# -----------------------------
# User Exceptions
# -----------------------------

app.add_exception_handler(
    UserNotFoundException,
    user_not_found_handler,
)

app.add_exception_handler(
    EmailAlreadyRegisteredException,
    email_already_registered_handler,
)


# -----------------------------
# Job Exceptions
# -----------------------------

app.add_exception_handler(
    JobNotFoundException,
    job_not_found_handler,
)

app.add_exception_handler(
    InvalidJobStatusTransitionException,
    invalid_job_status_transition_handler,
)


# -----------------------------
# Worker Exceptions
# -----------------------------

app.add_exception_handler(
    WorkerNotFoundException,
    worker_not_found_exception_handler,
)

app.add_exception_handler(
    WorkerAlreadyExistsException,
    worker_already_exists_exception_handler,
)


# -----------------------------
# Worker Skill Exceptions
# -----------------------------

app.add_exception_handler(
    WorkerSkillAlreadyExistsException,
    worker_skill_already_exists_handler,
)

app.add_exception_handler(
    WorkerSkillNotFoundException,
    worker_skill_not_found_handler,
)


# -----------------------------
# Assignment Exceptions
# -----------------------------

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


# -----------------------------
# Authorization Exception
# -----------------------------

app.add_exception_handler(
    PermissionDeniedException,
    permission_denied_handler,
)


# ============================================================
# API Routers
# ============================================================

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(workers_router)
app.include_router(skills_router)
app.include_router(assignments_router)
app.include_router(work_router)
app.include_router(evidence_router)
app.include_router(confirmation_router)
app.include_router(payment_router)
app.include_router(reputation_router)


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    """
    Basic health endpoint for the application.
    """

    return {
        "message": f"{settings.app_name} is running",
    }