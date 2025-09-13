# app/crud/note.py
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.models.note import Note, NoteStatus
# Schemas'ı doğrudan import et, içinden spesifik isimleri değil.
# Bu, döngüsel bağımlılık sorunlarını çözmeye yardımcı olabilir.
from app import schemas
# Python 3.10+ için Optional'ı import etmeye gerek yok ama eski sürümler için iyi bir pratik
# from pydantic import BaseModel de ekleyelim
from pydantic import BaseModel

def get_note(db: Session, *, note_id: int) -> Optional[Note]:
    """
    ID'ye göre bir notu getirir.
    """
    return db.query(Note).filter(Note.id == note_id).first()


def get_notes_by_user(
        db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
) -> List[Note]:
    """
    Belirli bir kullanıcıya ait notları listeler (sayfalama ile).
    """
    # En son oluşturulan notun en üstte görünmesi için sıralama ekleyelim
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
    Tüm notları listeler (sadece adminler için kullanılacak).
    """
    return (
        db.query(Note)
        .order_by(Note.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_note(db: Session, *, note_in: schemas.note.NoteCreate, owner_id: int) -> Note:
    """
    Belirli bir kullanıcı için yeni bir not oluşturur.
    """
    # note_in (Pydantic şeması) verilerini bir sözlüğe çeviriyoruz.
    # Bu sözlük sadece 'raw_text' içeriyor olacak.
    db_note = Note(**note_in.dict(), owner_id=owner_id)

    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


# === GÜNCELLENMİŞ FONKSİYON ===
def update_note(
        db: Session, *, db_note: Note, note_in: schemas.note.NoteUpdate | dict
) -> Note:
    """
    Bir notu günceller. Hem Pydantic şeması hem de sözlük kabul eder.
    Bu, worker'dan gelen güncellemeler için esneklik sağlar.
    """
    # Gelen veriyi Pydantic modeli ise sözlüğe çevir
    if isinstance(note_in, BaseModel):
        update_data = note_in.dict(exclude_unset=True)
    else:
        update_data = note_in

    # Mevcut db_note objesinin alanlarını gelen verilerle güncelle
    for field, value in update_data.items():
        setattr(db_note, field, value)

    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, *, note_id: int) -> Optional[Note]:
    """
    Bir notu siler. (Fonksiyonda değişiklik yok, sadece imza güncellendi)
    """
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note:
        db.delete(db_note)
        db.commit()
    return db_note



