# app/models/user.py
import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    """
    Enum for the possible roles a user can have.
    """
    ADMIN = "ADMIN"
    AGENT = "AGENT"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # The 'role' column uses the Enum type with a default value of AGENT.
    # Every new user will automatically be an AGENT unless specified otherwise.
    role = Column(Enum(UserRole), default=UserRole.AGENT, nullable=False)

    # Establishes a one-to-many relationship: one User can have many Notes.
    # 'back_populates' creates a bidirectional link with the 'owner' relationship in the Note model.
    notes = relationship("Note", back_populates="owner")