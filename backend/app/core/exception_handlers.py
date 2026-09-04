from fastapi import Request
from fastapi.responses import JSONResponse

from backend.app.core.exceptions import (
    UserNotFoundException,
    EmailAlreadyRegisteredException,
    JobNotFoundException,
    InvalidJobStatusTransitionException,
    WorkerNotFoundException,
    WorkerAlreadyExistsException,
)


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
            "detail": str(exc),
        },
    )


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