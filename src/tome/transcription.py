import os
import uuid
from sqlite3 import Connection, Cursor
from typing import cast
from uuid import UUID

import whisper
from whisper import Whisper

from .config import Config
from .database import get_transcription_by_hash_and_model, insert_row
from .fileactions import Segment, get_file_hash, write_transcript


def load_model(config: Config):
    return whisper.load_model(config["transcription_model"])


def transcribe_text(
    audio_location: str, model: Whisper, cur: Cursor, conn: Connection, config: Config
) -> tuple[str, UUID]:
    audio_hash = get_file_hash(audio_location, config)
    transcribe_row = get_transcription_by_hash_and_model(cur, audio_hash, config)
    if transcribe_row is None or not os.path.exists(str(transcribe_row["transcription_location"])):
        file_id = uuid.uuid4()
        transcription_location = write_transcript(
            cast(
                dict[str, list[Segment]],
                model.transcribe(audio_location, task="transcribe", beam_size=5, best_of=5, fp16=False),
            ),
            file_id,
            config,
        )
        transcription_hash = get_file_hash(transcription_location, config)
        insert_row(
            cur,
            conn,
            config["transcript_db_name"],
            {
                "audio_file_hash": audio_hash,
                "transcription_location": transcription_location,
                "transcription_hash": transcription_hash,
            },
            config,
        )
        print(f"Finished transcribing {transcription_location}!")
    else:
        transcription_location = str(transcribe_row["transcription_location"])
        file_id = os.path.splitext(os.path.basename(transcription_location))[0]
        print(f"Found transcription location: {transcription_location}!")

    return transcription_location, cast(UUID, file_id)
