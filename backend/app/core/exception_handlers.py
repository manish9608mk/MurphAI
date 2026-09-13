import logging

from fastapi import Request
from fastapi.responses import JSONResponse

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


logger = logging.getLogger(__name__)


# User Exception Handlers

async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "User not found",
        },
    )


async def email_already_registered_handler(
    request: Request,
    exc: EmailAlreadyRegisteredException,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Email already registered",
        },
    )


# Job Exception Handlers

async def job_not_found_handler(
    request: Request,
    exc: JobNotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Job not found",
        },
    )


async def invalid_job_status_transition_handler(
    request: Request,
    exc: InvalidJobStatusTransitionException,
):
    return JSONResponse(
        status_code=400,
        content={
            # Return the actual transition error to the client.
            "detail": str(exc),
        },
    )


# Worker Exception Handlers

async def worker_not_found_exception_handler(
    request: Request,
    exc: WorkerNotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Worker not found",
        },
    )


async def worker_already_exists_exception_handler(
    request: Request,
    exc: WorkerAlreadyExistsException,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Worker profile already exists for this user",
        },
    )


# Worker Skill Exception Handlers

async def worker_skill_already_exists_handler(
    request: Request,
    exc: WorkerSkillAlreadyExistsException,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Worker already has this skill",
        },
    )


async def worker_skill_not_found_handler(
    request: Request,
    exc: WorkerSkillNotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Worker skill not found",
        },
    )


# Assignment Exception Handlers

async def assignment_not_found_exception_handler(
    request: Request,
    exc: AssignmentNotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Assignment not found",
        },
    )


async def assignment_already_exists_exception_handler(
    request: Request,
    exc: AssignmentAlreadyExistsException,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Assignment already exists",
        },
    )


async def invalid_assignment_transition_handler(
    request: Request,
    exc: InvalidAssignmentTransitionException,
):
    return JSONResponse(
        status_code=400,
        content={
            # Return the actual assignment transition error.
            "detail": str(exc),
        },
    )


async def worker_unavailable_exception_handler(
    request: Request,
    exc: WorkerUnavailableException,
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Worker is currently unavailable",
        },
    )


# Permission Exception Handler

async def permission_denied_handler(
    request: Request,
    exc: PermissionDeniedException,
):
    return JSONResponse(
        status_code=403,
        content={
            # Return the permission reason to the client.
            "detail": str(exc),
        },
    )


# Unexpected Exception Handler

async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    # Log the real error internally without exposing details to users.
    logger.exception(
        "Unexpected application error | request_id=%s",
        request_id,
        exc_info=exc,
    )

    response = JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
        },
    )

    if request_id:
        response.headers["X-Request-ID"] = request_id

    return response
