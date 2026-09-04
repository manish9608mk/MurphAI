from fastapi import Request
from fastapi.responses import JSONResponse

from backend.app.core.exceptions import (
    UserNotFoundException,
    EmailAlreadyRegisteredException,
    JobNotFoundException,
)


async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "User not found"
        },
    )


async def email_already_registered_handler(
    request: Request,
    exc: EmailAlreadyRegisteredException,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Email already registered"
        },
    )


async def job_not_found_handler(
    request: Request,
    exc: JobNotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Job not found"
        },
    )