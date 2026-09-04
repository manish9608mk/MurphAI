from pydantic import BaseModel, ConfigDict, Field


class SkillCreate(BaseModel):
    # Name entered by the worker.
    #
    # Example:
    # "Electrician"
    name: str = Field(
        min_length=2,
        max_length=100,
    )


class SkillResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )