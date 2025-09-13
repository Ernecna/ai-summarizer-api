# app/schemas/note.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

from app.models.note import NoteStatus


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Schemas for Nested Objects
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class NoteOwnerPublic(BaseModel):
    """
    Publicly available information about a note's owner.
    Used for nesting within the main NotePublic schema.
    """
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Schemas for API Request Bodies
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class NoteCreate(BaseModel):
    """
    Schema for creating a new note (request body for POST /notes).
    """
    raw_text: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Text to be summarized. Must be between 50 and 5000 characters."
    )


class NoteUpdate(BaseModel):
    """
    Schema for updating a note (request body for PATCH /notes/{note_id}).
    Used for admin purposes, like requeueing a failed task.
    """
    raw_text: Optional[str] = Field(None, min_length=50, max_length=5000)
    status: Optional[NoteStatus] = Field(None, description="New status for the note.")


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Schemas for API Response Bodies
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class NotePublic(BaseModel):
    """
    The definitive public representation of a Note object in API responses.
    """
    id: int = Field(description="Unique ID of the note.")
    status: NoteStatus = Field(description="Current status of the summarization task.")
    raw_text: str = Field(description="The original text provided by the user.")
    summary: Optional[str] = Field(None, description="The generated summary. Null if not 'DONE'.")
    failure_reason: Optional[str] = Field(None, description="Reason for failure. Null if not 'FAILED'.")
    processing_time_ms: Optional[float] = Field(None, description="Time taken for summarization in milliseconds.")
    created_at: datetime = Field(description="Timestamp when the note was created.")
    owner: NoteOwnerPublic = Field(description="The user who created the note.")

    class Config:
        from_attributes = True