from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=100,
    )

    description: str = Field(
        min_length=10,
        max_length=2000,
    )

    location: str = Field(
        min_length=2,
        max_length=200,
    )

    budget: float = Field(
        gt=0,
    )


class JobUpdate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=100,
    )

    description: str = Field(
        min_length=10,
        max_length=2000,
    )

    location: str = Field(
        min_length=2,
        max_length=200,
    )

    budget: float = Field(
        gt=0,
    )


class JobStatusUpdate(BaseModel):
    status: str = Field(
        min_length=1,
        max_length=30,
    )


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    budget: float
    status: str
    customer_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )