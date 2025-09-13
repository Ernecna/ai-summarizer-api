# app/crud/note.py
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate # Direct, explicit imports

def get_note(db: Session, *, note_id: int) -> Optional[Note]:
    """
    Retrieves a single note by its ID.
    """
    return db.query(Note).filter(Note.id == note_id).first()


def get_notes_by_user(
    db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
) -> List[Note]:
    """
    Retrieves a list of notes for a specific user, with pagination.
    """
    return (
        db.query(Note)
        .filter(Note.owner_id == owner_id)
        .order_by(Note.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_notes(db: Session, *, skip: int = 0, limit: int = 100) -> List[Note]:
    """
    Retrieves a list of all notes in the system, with pagination. (For admins)
    """
    return (
        db.query(Note)
        .order_by(Note.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_note(db: Session, *, note_in: NoteCreate, owner_id: int) -> Note:
    """
    Creates a new note for a specific user.
    """
    db_note = Note(**note_in.dict(), owner_id=owner_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(
    db: Session, *, db_note: Note, note_in: NoteUpdate | dict
) -> Note:
    """
    Updates a note's details. Accepts either a Pydantic schema or a dict.
    This provides flexibility for updates coming from the API or background workers.
    """
    if isinstance(note_in, BaseModel):
        update_data = note_in.dict(exclude_unset=True)
    else:
        update_data = note_in

    for field, value in update_data.items():
        setattr(db_note, field, value)

    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, *, note_id: int) -> Optional[Note]:
    """
    Deletes a note from the database by its ID.
    """
    note_to_delete = db.query(Note).filter(Note.id == note_id).first()
    if note_to_delete:
        db.delete(note_to_delete)
        db.commit()
    return note_to_delete