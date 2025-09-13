# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.dependencies import get_db
from app.crud import user as crud_user
from app.schemas import user as user_schema
from app.schemas import token as token_schema

router = APIRouter()


@router.post("/register", response_model=user_schema.UserResponse)
def register_user(
        *,
        db: Session = Depends(get_db),
        user_in: user_schema.UserCreate,
):
    """
    Yeni kullanıcı kaydı. Varsayılan rol AGENT'tır.
    """
    # ... (debug print'lerini silebilirsin artık)
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(...)
    user = crud_user.create_user(db, user_in=user_in)
    return user


@router.post("/login", response_model=token_schema.Token)
def login_for_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Kullanıcı girişi ve JWT token'ı oluşturma.
    OAuth2PasswordRequestForm, 'username' ve 'password' alanlarını bekler.
    """
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token = security.create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}
