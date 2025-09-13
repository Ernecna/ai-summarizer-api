# app/crud/user.py
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieves a single user by their ID.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, *, email: str) -> Optional[User]:
    """
    Retrieves a single user by their email address.
    """
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieves a list of users, with pagination.
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, *, user_in: UserCreate) -> User:
    """
    Creates a new user in the database.
    """
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role,
        is_active=user_in.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, *, db_user: User, user_in: UserUpdate) -> User:
    """
    Updates a user's details in the database.
    """
    update_data = user_in.dict(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, *, user_id: int) -> Optional[User]:
    """
    Deletes a user from the database by their ID.
    """
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if user_to_delete:
        db.delete(user_to_delete)
        db.commit()
    return user_to_delete