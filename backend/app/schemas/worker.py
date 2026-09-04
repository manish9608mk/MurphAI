from pydantic import BaseModel, ConfigDict, Field


class WorkerCreate(BaseModel):
    bio: str | None = Field(
        default=None,
        max_length=2000,
    )

    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    experience_years: int = Field(
        default=0,
        ge=0,
        le=60,
    )

    is_available: bool = True


class WorkerUpdate(BaseModel):
    bio: str | None = Field(
        default=None,
        max_length=2000,
    )

    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    experience_years: int = Field(
        default=0,
        ge=0,
        le=60,
    )

    is_available: bool = True


class WorkerResponse(BaseModel):
    id: int
    user_id: int
    bio: str | None
    location: str | None
    experience_years: int
    is_available: bool

    model_config = ConfigDict(
        from_attributes=True,
    )