from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.schemas.auth import UserRegister, UserLogin

from backend.app.core.exceptions import (
    EmailAlreadyRegisteredException,
)

from backend.app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def register_user(
    db: Session,
    user_data: UserRegister,
):
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        raise EmailAlreadyRegisteredException()

    return user


def login_user(
    db: Session,
    user_data: UserLogin,
):
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if not user:
        return None

    password_valid = verify_password(
        user_data.password,
        user.password_hash,
    )

    if not password_valid:
        return None

    access_token = create_access_token(
        user_id=user.id,
    )

    return access_token
