
import time
import logging
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from app.core.database import SessionLocal
from app.crud.note import get_note, update_note
from app.models.note import NoteStatus

# ===============================================================
#  LOGGING VE MODEL YÜKLEME (WORKER BAŞLADIĞINDA BİR KEZ ÇALIŞIR)
# ===============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cihazı belirle: Varsa CUDA (NVIDIA GPU) kullan, yoksa CPU kullan.
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

# Modeli ve tokenizer'ı global olarak yükle. Bu, her görevde tekrar yüklemeyi önler.
try:
    logger.info("Loading T5 model and tokenizer from local cache...")
    # model_path = "/app/model_cache" # Eski, sadece Docker için geçerli
    model_path = "./model_cache" # YENİ, hem local hem Docker için çalışır (çünkü worker kök dizinden çalıştırılıyor)
    tokenizer = T5Tokenizer.from_pretrained(model_path)
    model = T5ForConditionalGeneration.from_pretrained(model_path).to(device)
    # ...
except Exception as e:
    logger.error(f"Failed to load T5 model: {e}", exc_info=True)
    # Model yüklenemezse, worker'ın başlamasını engellemek için hata fırlat
    # veya görevlerin anında FAILED durumuna düşmesini sağla.
    tokenizer = None
    model = None

# ===============================================================
#  RQ GÖREV FONKSİYONU
# ===============================================================

def summarize_text_task(note_id: int):
    """
    Bir notun özetleme işlemini yapacak olan arka plan görevi (T5 entegrasyonu ile).
    """
    logger.info(f"Task started for note_id: {note_id}")

    # Model yüklenemediyse görevi hemen başarısız olarak işaretle
    if not model or not tokenizer:
        db = SessionLocal()
        note = get_note(db, note_id=note_id)
        if note:
            error_msg = "AI model is not available. Task cannot be processed."
            update_note(db, db_note=note, note_in={"status": NoteStatus.FAILED, "failure_reason": error_msg})
        db.close()
        logger.error(error_msg)
        return

    db = SessionLocal()
    try:
        note = get_note(db, note_id=note_id)
        if not note:
            logger.error(f"Note with id {note_id} not found.")
            return

        # 1. Durumu 'PROCESSING' olarak güncelle
        update_note(db, db_note=note, note_in={"status": NoteStatus.PROCESSING})

        # 2. GERÇEK T5 MODELİNİ ÇALIŞTIRMA
        start_time = time.time()

        # T5 için metni hazırla
        input_text = "summarize: " + note.raw_text
        input_ids = tokenizer.encode(
            input_text, return_tensors="pt", max_length=1024, truncation=True
        ).to(device) # Veriyi GPU/CPU'ya gönder

        # Modeli kullanarak özeti oluştur
        summary_ids = model.generate(
            input_ids,
            max_length=150,
            min_length=40,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True,
        )
        summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        end_time = time.time()
        processing_time = (end_time - start_time) * 1000

        # 3. Sonucu ve metrikleri veritabanına kaydet
        logger.info(f"Summarization for note {note_id} DONE in {processing_time:.2f} ms.")
        update_data = {
            "status": NoteStatus.DONE,
            "summary": summary_text,
            "processing_time_ms": processing_time,
            "failure_reason": None # Başarılı olduğu için önceki hatayı temizle
        }
        update_note(db, db_note=note, note_in=update_data)

    except Exception as e:
        logger.error(f"Task failed for note {note_id}: {e}", exc_info=True)
        # Hata durumunda veritabanını güncelle
        if 'note' in locals() and note: # 'note' değişkeni tanımlanmışsa
             update_note(db, db_note=note, note_in={"status": NoteStatus.FAILED, "failure_reason": str(e)[:512]})

    finally:
        logger.info(f"Closing DB session for note_id: {note_id}")
        db.close()