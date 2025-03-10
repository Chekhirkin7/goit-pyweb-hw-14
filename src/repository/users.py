from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


def get_user_by_email(email: str, db: Session):
    """
    Fetch user by email from the database.

    :param email: User's email
    :param db: SQLAlchemy session
    :return: User object if found, None otherwise
    """

    stmt = select(User).filter(User.email == email)
    user = db.execute(stmt)
    return user.scalar_one_or_none()


def create_user(body: UserSchema, db: Session):
    """
    Create a new user in the database.

    :param body: User data
    :param db: SQLAlchemy session
    :return: Newly created user object
    """

    new_user = User(**body.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_token(user: User, token: str | None, db: Session):
    """
    Update user's refresh token.

    :param user: User object
    :param token: New refresh token
    :param db: SQLAlchemy session
    :return:
    """

    user.refresh_token = token
    db.commit()

def confirmed_email(email: str, db: Session):
    """
    Confirm user's email address.

    :param email: User's email
    :param db: SQLAlchemy session
    :return:
    """

    user = get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
