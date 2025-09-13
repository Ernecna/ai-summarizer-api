# app/api/v1/notes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.crud import note as crud_note
from app.models.user import User, UserRole  # Import UserRole Enum
from app.schemas.note import NoteCreate, NotePublic
from app.tasks.queue import q
from app.tasks.summarize_task import summarize_text_task

router = APIRouter()


@router.post("/", response_model=NotePublic, status_code=status.HTTP_201_CREATED)
def create_new_note(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    note_in: NoteCreate,
):
    """
    Create a new note and enqueue it for summarization.

    - Any authenticated and active user (AGENT or ADMIN) can create a note.
    - The note is saved to the database with a 'QUEUED' status.
    - A background job is enqueued to Redis to process the summarization.
    - The initial state of the note is returned immediately to the user.
    """
    note = crud_note.create_note(db=db, note_in=note_in, owner_id=current_user.id)
    q.enqueue(summarize_text_task, note.id)
    return note


@router.get("/{note_id}", response_model=NotePublic)
def get_note_by_id(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    note_id: int,
):
    """
    Retrieve the details of a specific note, including its status and summary.

    - AGENTs can only retrieve notes they own.
    - ADMINs can retrieve any note.
    """
    note = crud_note.get_note(db=db, note_id=note_id)

    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    # Authorization check
    if current_user.role != UserRole.ADMIN and note.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this note.",
        )

    return note


@router.get("/", response_model=List[NotePublic])
def list_notes(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    List notes with pagination.

    - AGENTs will see a list of their own notes.
    - ADMINs will see a list of all notes in the system.
    """
    if current_user.role == UserRole.ADMIN:
        notes = crud_note.get_all_notes(db, skip=skip, limit=limit)
    else:  # AGENT
        notes = crud_note.get_notes_by_user(
            db, owner_id=current_user.id, skip=skip, limit=limit
        )

    return notes