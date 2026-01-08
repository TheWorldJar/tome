from sqlite3 import Connection, Cursor
from uuid import UUID

import ollama
from ollama import GenerateResponse

from .config import Config
from .database import get_note_by_hash, insert_row, update_note
from .fileactions import get_file_hash, read_file, write_note


def get_ollama_response(
    cur: Cursor,
    conn: Connection,
    transcription_location: str,
    prompt_location: str,
    file_id: UUID,
    config: Config,
):
    transcription_content = read_file(transcription_location)
    transcription_hash = get_file_hash(transcription_location, config)
    prompt_content = read_file(prompt_location)

    # TODO: verify that transcription_content and prompt_content are not None

    res: GenerateResponse = ollama.generate(
        model=config["output_model"],
        prompt=f"{prompt_content}\n\n## FILE CONTENT:\n{transcription_content}",
        keep_alive=0,
    )
    note_location = write_note(res.response, file_id, config)
    note_hash = get_file_hash(note_location, config)

    note_row = get_note_by_hash(cur, transcription_hash, config)
    if note_row is None:
        insert_row(
            cur,
            conn,
            config["notes_db_name"],
            {
                "transcription_location": transcription_location,
                "transcription_hash": transcription_hash,
                "note_location": note_location,
                "note_hash": note_hash,
            },
            config,
        )
    else:
        update_note(
            cur,
            conn,
            transcription_hash,
            {
                "transcription_location": transcription_location,
                "note_location": note_location,
                "note_hash": note_hash,
            },
            config,
        )
    return note_location
