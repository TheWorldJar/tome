import os
import uuid

import whisper

from src.const import TRANSCRIBE_MODEL, TRANSCRIBE_DB_NAME
from src.database import get_transcription_by_hash, insert_row
from src.fileactions import write_transcript, get_file_hash


def load_model():
    return whisper.load_model(TRANSCRIBE_MODEL)


def transcribe_text(audio_location, model, cur, conn):
    options = {
        "language": "en",
        "task": "transcribe",
        "beam_size": 5,
        "best_of": 5,
        "fp16": False,
    }

    audio_hash = get_file_hash(audio_location)
    transcribe_row = get_transcription_by_hash(cur, audio_hash)
    if transcribe_row is None or not os.path.exists(
        transcribe_row["transcription_location"]
    ):
        file_id = uuid.uuid4()
        transcription_location = write_transcript(
            model.transcribe(audio_location, **options),
            file_id,
        )
        transcription_hash = get_file_hash(transcription_location)
        insert_row(
            cur,
            conn,
            TRANSCRIBE_DB_NAME,
            {
                "audio_file_hash": audio_hash,
                "transcription_location": transcription_location,
                "transcription_hash": transcription_hash,
            },
        )
        print(f"Finished transcribing {transcription_location}!")
    else:
        transcription_location = transcribe_row["transcription_location"]
        file_id = os.path.splitext(os.path.basename(transcription_location))[0]
        print(f"Found transcription location: {transcription_location}!")

    return transcription_location, file_id
