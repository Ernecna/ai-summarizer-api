# app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user, get_current_admin_user
from app.crud import user as crud_user
from app.models.user import User
from app.schemas import user as user_schema
from typing import List

router = APIRouter()


@router.get("/me", response_model=user_schema.UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Mevcut giriş yapmış kullanıcının bilgilerini getirir.
    """
    return current_user


@router.get("/{user_id}", response_model=user_schema.UserResponse)
def read_user_by_id(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user),  # Sadece adminler erişebilir
):
    """
    ID'ye göre bir kullanıcıyı getirir (Admin yetkisi gerektirir).
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/", response_model=List[user_schema.UserResponse])
def read_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user),  # <-- Sadece adminler!
):
    """
    Kullanıcıların bir listesini getirir (Admin yetkisi gerektirir).
    """
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users


def delete_user(db: Session, *, user_id: int) -> User | None:
    """
    ID'si verilen bir kullanıcıyı veritabanından siler.
    """
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if user_to_delete:
        db.delete(user_to_delete)
        db.commit()
    return user_to_delete
