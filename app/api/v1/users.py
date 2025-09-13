# app/api/v1/users.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user, get_current_admin_user
from app.crud import user as crud_user
from app.models.user import User
from app.schemas import user as user_schema

router = APIRouter()


@router.get("/me", response_model=user_schema.UserPublic)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """
    Get the profile of the currently logged-in user.
    """
    return current_user


@router.get("/", response_model=List[user_schema.UserPublic])
def list_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user),
):
    """
    Retrieve a list of users. (Admins only)
    """
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=user_schema.UserPublic)
def read_user_by_id(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user),
):
    """
    Get a specific user by their ID. (Admins only)
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=user_schema.UserPublic)
def delete_user_by_id(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user),
):
    """
    Delete a specific user by their ID. (Admins only)
    """
    user_to_delete = crud_user.get_user(db, user_id=user_id)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if current_user.id == user_to_delete.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot delete their own account.",
        )

    deleted_user = crud_user.delete_user(db, user_id=user_id)
    return deleted_user
