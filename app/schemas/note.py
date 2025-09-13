# app/schemas/note.py
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from app.models.note import NoteStatus  # Bu import kritik


# ===============================================================
#  İÇ İÇE (NESTED) ŞEMALAR
# ===============================================================
# Notun sahibine dair herkese açık bilgiler
class NoteOwnerPublic(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


# ===============================================================
#  API İSTEK (REQUEST) GÖVDELERİ İÇİN ŞEMALAR
# ===============================================================
# POST /notes için kullanıcıdan alınacak tek bilgi
class NoteCreate(BaseModel):
    raw_text: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Text to be summarized. Should be between 50 and 5000 characters."
    )


# BİR NOTU GÜNCELLEME İSTEĞİ (PATCH /notes/{note_id})
# Bu şemayı eklemeyi unutmuşuz. crud/note.py bu şemaya ihtiyaç duyuyor.
class NoteUpdate(BaseModel):
    raw_text: Optional[str] = Field(None, min_length=50, max_length=5000)
    # Bir adminin FAILED durumundaki bir görevi yeniden QUEUED yapması gibi durumlar için:
    status: Optional[NoteStatus] = None


# ===============================================================
#  API YANIT (RESPONSE) GÖVDELERİ İÇİN ŞEMALAR
# ===============================================================
# GET /notes/{id} veya POST /notes yanıtı olarak dönecek olan,
# herkese açık ve zenginleştirilmiş Not bilgisi.
class NotePublic(BaseModel):
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
