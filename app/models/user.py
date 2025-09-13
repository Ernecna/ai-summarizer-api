# app/models/user.py
import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


# User rolleri için bir Enum tanımlıyoruz.
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    AGENT = "AGENT"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Rol sütununu Enum tipinde ve varsayılan değeri AGENT olarak ekliyoruz.
    # Yeni kaydolan her kullanıcı, biz aksini belirtmedikçe otomatik olarak AGENT olacak.
    role = Column(Enum(UserRole), default=UserRole.AGENT, nullable=False)

    # İlişki tanımı (değişiklik yok)
    notes = relationship("Note", back_populates="owner")