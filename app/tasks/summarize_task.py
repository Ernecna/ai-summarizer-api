# app/tasks/summarize_task.py
import os
import time
import logging
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

from app.core.database import SessionLocal
from app.crud.note import get_note, update_note
from app.models.note import NoteStatus

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Setup: Logging, Device, and Model Configuration
# This part runs once when the worker process starts.
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Determine the device to run the model on (GPU if available, otherwise CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Worker using device: {device}")

# Model configuration
MODEL_NAME = "t5-small"
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "./model_cache")  # Flexible path

# Global variables for the loaded model and tokenizer
tokenizer = None
model = None

try:
    logger.info(f"Loading tokenizer and model from: {MODEL_CACHE_DIR}")
    # This assumes the model has been downloaded to this path,
    # either by a pre-run script or by a previous worker run.
    tokenizer = T5Tokenizer.from_pretrained(MODEL_CACHE_DIR)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_CACHE_DIR).to(device)
    logger.info("Model and tokenizer loaded successfully.")
except OSError:
    logger.error(
        f"Model not found in cache directory: {MODEL_CACHE_DIR}. "
        "The worker will mark tasks as FAILED until the model is available. "
        "Run 'python download_model.py' locally or ensure the Docker build process completes."
    )
except Exception as e:
    logger.error(f"An unexpected error occurred while loading the model: {e}", exc_info=True)


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# The main RQ task function
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def summarize_text_task(note_id: int):
    """
    The background task that performs summarization on a note using a T5 model.
    This function is executed by an RQ worker.
    """
    logger.info(f"Processing task for note_id: {note_id}")

    # Fail fast if the model could not be loaded on worker startup
    if not model or not tokenizer:
        db = SessionLocal()
        note = get_note(db, note_id=note_id)
        if note:
            error_msg = "AI model is not available on the worker."
            update_note(db, db_note=note, note_in={"status": NoteStatus.FAILED, "failure_reason": error_msg})
        db.close()
        logger.error(f"Task for note {note_id} failed: {error_msg}")
        return

    db = SessionLocal()
    try:
        note = get_note(db, note_id=note_id)
        if not note:
            logger.warning(f"Note with id {note_id} not found in database. Task may be stale.")
            return

        # 1. Update status to PROCESSING
        update_note(db, db_note=note, note_in={"status": NoteStatus.PROCESSING})

        # 2. Perform the actual AI summarization
        start_time = time.time()

        input_text = "summarize: " + note.raw_text
        input_ids = tokenizer(input_text, return_tensors="pt", max_length=1024, truncation=True).input_ids.to(device)

        summary_ids = model.generate(
            input_ids,
            max_length=150,
            min_length=30,
            num_beams=4,
            early_stopping=True,
        )
        summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        end_time = time.time()
        processing_time = (end_time - start_time) * 1000

        # 3. Save the successful result to the database
        logger.info(f"Summarization for note {note_id} completed in {processing_time:.2f} ms.")
        update_data = {
            "status": NoteStatus.DONE,
            "summary": summary_text,
            "processing_time_ms": processing_time,
            "failure_reason": None,
        }
        update_note(db, db_note=note, note_in=update_data)

    except Exception as e:
        logger.error(f"An error occurred during summarization for note {note_id}: {e}", exc_info=True)
        if 'note' in locals() and note:
            update_note(db, db_note=note, note_in={"status": NoteStatus.FAILED, "failure_reason": str(e)[:512]})

    finally:
        logger.info(f"DB session closed for note_id: {note_id}")
        db.close()