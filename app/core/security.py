# app/core/security.py

from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# 1. Şifre Yönetimi
# Hangi hashing algoritmasını kullanacağımızı belirtiyoruz. Bcrypt endüstri standardıdır.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY


def create_access_token(subject: Union[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Verilen kimlik (subject) için yeni bir JWT access token oluşturur.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Eğer süre belirtilmezse, config dosyasındaki varsayılan süreyi kullan
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Düz metin şifre ile hashlenmiş şifrenin eşleşip eşleşmediğini kontrol eder.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Verilen düz metin şifreyi hash'ler.
    """
    return pwd_context.hash(password)