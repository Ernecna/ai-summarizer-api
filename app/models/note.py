# app/models/note.py
import enum
from sqlalchemy import (Column, Integer, Text, ForeignKey, DateTime,
                        Enum, String, Float)  # Float'ı ekledik
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class NoteStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)

    # Girdi ve Çıktı Alanları
    raw_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    # Süreç Yönetimi ve İzleme Alanları
    status = Column(Enum(NoteStatus), default=NoteStatus.QUEUED, nullable=False, index=True)
    processing_time_ms = Column(Float, nullable=True)  # YENİ: Modelin ne kadar sürede çalıştığını izlemek için.
    failure_reason = Column(String(512), nullable=True)  # YENİ: Hata mesajlarını saklamak için.

    # Zaman Damgaları ve Sahiplik
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # SQLAlchemy İlişkisi
    owner = relationship("User", back_populates="notes")