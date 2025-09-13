# app/core/dependencies.py
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.crud import user as crud_user
from app.models.user import User, UserRole
from app.schemas.token import TokenData


# 1. Veritabanı Oturumu Bağımlılığı (daha önce database.py'deydi, burada olması daha uygun)
def get_db() -> Generator:
    # === HATA AYIKLAMA İÇİN BUNU EKLE ===
    print(">>> get_db fonksiyonu çağrıldı, session oluşturuluyor.")
    # ====================================
    db = SessionLocal()
    try:
        # === HATA AYIKLAMA İÇİN BUNU EKLE ===
        print(">>> Session oluşturuldu, endpoint'e veriliyor (yield).")
        # ====================================
        yield db
    finally:
        # === HATA AYIKLAMA İÇİN BUNU EKLE ===
        print(">>> Endpoint çalışması bitti, session kapatılıyor.")
        # ====================================
        db.close()



# 2. OAuth2 Şeması
# FastAPI'ye token'ın nereden alınacağını söylüyoruz.
# tokenUrl, token'ı almak için gidilecek endpoint'in adresidir.
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


# 3. Mevcut Kullanıcıyı Getiren Ana Bağımlılık
def get_current_user(
        db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """
    Token'ı doğrular ve veritabanından ilgili kullanıcıyı getirir.
    """
    try:
        # Token'ı decode etmeye çalış. SECRET_KEY ve ALGORITHM ile doğrula.
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Token içeriğini (payload) TokenData şeması ile doğrula
        token_data = TokenData(email=payload.get("sub"))
        if token_data.email is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except (JWTError, ValidationError):
        # Eğer token geçersizse (süresi dolmuş, imzası yanlış vb.) hata fırlat.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token geçerliyse, içindeki e-posta adresiyle veritabanından kullanıcıyı bul.
    user = crud_user.get_user_by_email(db, email=token_data.email)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


# 4. Yetkilendirme Bağımlılıkları (Mevcut kullanıcıyı alıp rollerini kontrol eder)
def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    Mevcut kullanıcının aktif olup olmadığını kontrol eder.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def get_current_admin_user(
        current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Mevcut aktif kullanıcının ADMIN rolünde olup olmadığını kontrol eder.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_agent_user(
        current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Mevcut aktif kullanıcının AGENT rolünde olup olmadığını kontrol eder.
    """
    if current_user.role != UserRole.AGENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user