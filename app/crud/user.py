# app/crud/user.py
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.models import note # Note modelini import et
from typing import List

def get_user_by_email(db: Session, *, email: str) -> User | None:
    """
    E-posta adresine göre bir kullanıcıyı getirir.
    """
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int) -> User | None:
    """
    ID'ye göre bir kullanıcıyı getirir.
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, *, user_in: UserCreate) -> User:
    """
    Yeni bir kullanıcı oluşturur.
    """
    # Gelen şifreyi hash'le
    hashed_password = get_password_hash(user_in.password)

    # UserCreate şemasından gelen verilerle bir ORM modeli oluştur
    # Pydantic'in .dict() metodu, şema verilerini sözlüğe çevirir
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role,
        is_active=user_in.is_active
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user) # Veritabanından gelen ID gibi yeni verileri objeye yükle
    return db_user

def update_user(db: Session, *, db_user: User, user_in: UserUpdate) -> User:
    """
    Bir kullanıcının bilgilerini günceller.
    """
    # Gelen güncelleme verilerini (user_in) sözlüğe çevir.
    # exclude_unset=True, sadece gönderilen (None olmayan) alanları alır.
    update_data = user_in.dict(exclude_unset=True)

    # Eğer yeni bir şifre gönderildiyse, onu hash'le
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"] # Düz metin şifreyi sil

    # db_user objesinin alanlarını gelen verilerle güncelle
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Kullanıcıları listeler (sayfalama ile).

    Args:
        db: SQLAlchemy veritabanı oturumu.
        skip: Atlanacak kullanıcı sayısı.
        limit: Döndürülecek maksimum kullanıcı sayısı.

    Returns:
        Veritabanından alınan User objelerinin bir listesi.
    """
    return db.query(User).offset(skip).limit(limit).all()

def delete_user(db: Session, *, user_id: int) -> User | None:
    """
    ID'si verilen bir kullanıcıyı veritabanından siler.
    """
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if user_to_delete:
        db.delete(user_to_delete)
        db.commit()
    return user_to_delete