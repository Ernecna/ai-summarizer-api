# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole  # Modellerimizdeki Enum'ı kullanıyoruz
from typing import List
from app.schemas.note import NotePublic

# --- Temel Şema ---
# Diğer şemaların miras alacağı ortak alanları içerir.
class UserBase(BaseModel):
    email: EmailStr
    is_active: bool | None = True


# --- İstek (Request) Şemaları ---
# API'ye veri gönderilirken kullanılacak şemalar

# Yeni kullanıcı oluşturma (kayıt olma)
class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.AGENT  # Varsayılan rol


# Admin tarafından kullanıcı güncellerken
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None
    role: UserRole | None = None


# --- Veritabanı (Internal) Şeması ---
# CRUD operasyonlarında kullanılacak, hashlenmiş şifreyi de içeren şema.
# API'ye asla doğrudan dönülmemeli.
class UserInDB(UserBase):
    id: int
    hashed_password: str
    role: UserRole

    class Config:
        from_attributes = True  # SQLAlchemy modeli ile Pydantic'i eşleştirir


# --- Yanıt (Response) Şeması ---
# API'den dışarıya veri dönerken kullanılacak güvenli şema.
# Şifre gibi hassas bilgileri içermez.
# --- ŞİMDİ UserResponse'u GÜNCELLEYELİM ---
class UserResponse(UserBase):
    id: int
    role: UserRole
    notes: List[NotePublic] = []  # User'a ait notların listesi

    class Config:
        from_attributes = True
