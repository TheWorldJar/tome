import ollama
from ollama import GenerateResponse

from src.const import NOTE_MODEL, NOTES_DB_NAME
from src.database import get_note_by_hash, insert_row, update_note
from src.fileactions import read_file, get_file_hash, write_note


def get_ollama_response(cur, conn, transcription_location, prompt_location, file_id):
    transcription_content = read_file(transcription_location)
    transcription_hash = get_file_hash(transcription_location)
    prompt_content = read_file(prompt_location)

    res: GenerateResponse = ollama.generate(
        model=NOTE_MODEL,
        prompt=f"{prompt_content}\n\nFILE CONTENT:\n{transcription_content}",
        keep_alive=0,
    )
    note_location = write_note(res.response, file_id)
    note_hash = get_file_hash(note_location)

    note_row = get_note_by_hash(cur, transcription_hash)
    if note_row is None:
        insert_row(
            cur,
            conn,
            NOTES_DB_NAME,
            {
                "transcription_location": transcription_location,
                "transcription_hash": transcription_hash,
                "note_location": note_location,
                "note_hash": note_hash,
            },
        )
    else:
        update_note(
            cur,
            transcription_hash,
            {
                "transcription_location": transcription_location,
                "note_location": note_location,
                "note_hash": note_hash,
            },
        )
    return note_location
