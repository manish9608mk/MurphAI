from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=50,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100,
    )


class UserUpdate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=50,
    )

    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True