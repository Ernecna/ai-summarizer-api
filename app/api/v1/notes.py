# app/api/v1/notes.py
# app/api/v1/notes.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Projemizin diğer katmanlarından gerekli modülleri import ediyoruz
from app.core.dependencies import get_db, get_current_active_user
from app.models.user import User
from app.schemas.note import NoteCreate, NotePublic
from app.crud import note as crud_note
from app.crud.note import create_note

# RQ kuyruğunu ve görev fonksiyonunu import ediyoruz
from app.tasks.queue import q
from app.tasks.summarize_task import summarize_text_task

router = APIRouter()


@router.post("/", response_model=NotePublic, status_code=status.HTTP_201_CREATED)
def create_new_note(
        *,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),  # Sadece giriş yapmış ve aktif kullanıcılar
        note_in: NoteCreate,
):
    """
    Yeni bir not oluşturur ve özetleme için kuyruğa alır.
    - Sadece giriş yapmış ve aktif kullanıcılar (AGENT veya ADMIN) not oluşturabilir.
    - Not veritabanına 'QUEUED' durumuyla kaydedilir.
    - Özetleme görevi Redis kuyruğuna atılır.
    - Kullanıcıya anında, notun ilk hali döndürülür.
    """
    # 1. Notu veritabanına 'QUEUED' durumuyla kaydet
    note = crud_note.create_note(db=db, note_in=note_in, owner_id=current_user.id)

    # 2. Özetleme görevini, notun ID'si ile birlikte RQ kuyruğuna at
    q.enqueue(summarize_text_task, note.id)

    # 3. Kullanıcıyı bekletmeden, oluşturulan notun objesini anında dön
    return note


@router.get("/{note_id}", response_model=NotePublic)
def get_note_by_id(
        *,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
        note_id: int,
):
    """
    ID'ye göre bir notun detaylarını, durumunu ve özetini getirir.
    - AGENT rolündeki kullanıcılar sadece kendi notlarını görebilir.
    - ADMIN rolündeki kullanıcılar herhangi bir notu görebilir.
    """
    note = crud_note.get_note(db=db, note_id=note_id)

    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    # Yetkilendirme Kontrolü
    if current_user.role != "ADMIN" and note.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this note")

    return note


@router.get("/", response_model=List[NotePublic])
def get_user_notes(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
        skip: int = 0,
        limit: int = 100,
):
    """
    Giriş yapmış kullanıcının notlarını listeler.
    - AGENT rolündeki kullanıcılar sadece kendi notlarını görür.
    - ADMIN rolündeki kullanıcılar tüm notları görür.
    """
    if current_user.role == "ADMIN":
        notes = crud_note.get_all_notes(db, skip=skip, limit=limit)
    else:  # AGENT
        notes = crud_note.get_notes_by_user(db, owner_id=current_user.id, skip=skip, limit=limit)

    return notes