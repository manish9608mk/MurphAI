from fastapi import FastAPI

from backend.app.core.config import settings

from backend.app.api.users import router as users_router
from backend.app.api.auth import router as auth_router
from backend.app.api.jobs import router as jobs_router

from backend.app.core.exceptions import (
    UserNotFoundException,
    EmailAlreadyRegisteredException,
    JobNotFoundException,
    InvalidJobStatusTransitionException,
)

from backend.app.core.exception_handlers import (
    user_not_found_handler,
    email_already_registered_handler,
    job_not_found_handler,
    invalid_job_status_transition_handler,
)


app = FastAPI(
    title="MurphAI",
    description="AI-powered intelligent system",
    version="0.1.0",
)


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


app.include_router(users_router)
app.include_router(auth_router)
app.include_router(jobs_router)


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} is running",
    }