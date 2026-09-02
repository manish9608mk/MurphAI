from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserUpdate

from backend.app.core.exceptions import (
    UserNotFoundException,
    EmailAlreadyRegisteredException,
)


def create_user(db: Session, user_data: UserCreate):
    user = User(
        name=user_data.name,
        email=user_data.email,
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

        raise EmailAlreadyRegisteredException()

    return user


def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise UserNotFoundException()

    return user


def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate,
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise UserNotFoundException()

    user.name = user_data.name
    user.email = user_data.email

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

        raise EmailAlreadyRegisteredException()

    return user


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise UserNotFoundException()

    db.delete(user)
    db.commit()