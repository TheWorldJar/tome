import os

import whisper

from src.fileactions import write_transcript, get_file_hash
from src.const import TRANSCRIBE_MODEL, TRANSCRIBE_DB_NAME
from src.database import get_transcription_by_hash, insert_row


def load_model():
    return whisper.load_model(TRANSCRIBE_MODEL)


async def transcribe_text(audio_location, model, cur):
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
        transcription_location = write_transcript(
            await model.transcribe(audio_location, **options)
        )
        transcription_hash = get_file_hash(transcription_location)
        insert_row(
            cur,
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
        print(f"Found transcription location: {transcription_location}!")

    return transcription_location
