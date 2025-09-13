# app/schemas/user.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole
# We will use a forward reference for NotePublic to avoid circular imports
from app.schemas.note import NotePublic


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Base Schema
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class UserBase(BaseModel):
    """
    Base schema for a user, containing common attributes.
    """
    email: EmailStr
    is_active: Optional[bool] = True


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Schemas for API Request Bodies
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class UserCreate(UserBase):
    """
    Schema for creating a new user (e.g., during registration).
    """
    password: str
    role: UserRole = UserRole.AGENT


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user. All fields are optional.
    """
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Schemas for Internal Use (e.g., in CRUD operations)
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class UserInDB(UserBase):
    """
    Schema representing a user as stored in the database, including hashed password.
    This schema should NEVER be returned in an API response.
    """
    id: int
    hashed_password: str
    role: UserRole

    class Config:
        from_attributes = True


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Schemas for API Response Bodies
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class UserPublic(UserBase):
    """
    Publicly available user information. This schema is safe to return in API responses.
    It includes a list of the user's notes.
    """
    id: int
    role: UserRole
    notes: List[NotePublic] = []

    class Config:
        from_attributes = True