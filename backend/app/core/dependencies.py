from fastapi import Depends, HTTPException, status

from backend.app.core.security import get_current_user_id
from backend.app.database.database import SessionLocal


def get_db():
    """
    Provide a database session for each request.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def verify_user_access(action: str):
    """
    Verify that the authenticated user owns the requested user resource.
    """

    def dependency(
        user_id: int,
        current_user_id: int = Depends(get_current_user_id),
    ):
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not allowed to {action} this user",
            )

        return current_user_id

    return dependency