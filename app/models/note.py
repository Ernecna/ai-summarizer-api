# app/models/note.py
import enum
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime,
    Enum,
    String,
    Float,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class NoteStatus(str, enum.Enum):
    """
    Enum for the possible statuses of a summarization task.
    """
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)

    # Input and Output Fields
    raw_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    # Process Management and Monitoring Fields
    status = Column(Enum(NoteStatus), default=NoteStatus.QUEUED, nullable=False, index=True)
    processing_time_ms = Column(Float, nullable=True)  # Time taken by the AI model in ms
    failure_reason = Column(String(512), nullable=True) # Stores error messages on failure

    # Timestamps and Ownership
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # SQLAlchemy Relationship
    # Establishes a bidirectional relationship with the User model.
    owner = relationship("User", back_populates="notes")