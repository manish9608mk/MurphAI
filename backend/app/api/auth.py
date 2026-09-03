from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
)

from backend.app.services.auth_service import (
    register_user,
    login_user,
)

from backend.app.core.dependencies import get_db


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    user = register_user(
        db,
        user_data,
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    access_token = login_user(
        db,
        user_data,
    )

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }