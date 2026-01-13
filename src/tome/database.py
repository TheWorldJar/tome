import os
import sqlite3
import time
import uuid
from sqlite3 import Connection, Cursor
from typing import TypedDict, cast

from .config import Config

TRANSCRIBE_SCHEMA = (
    "(id TEXT PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
    + "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, audio_file_hash TEXT NOT NULL, "
    + "transcription_location TEXT, transcription_hash TEXT, model TEXT NOT NULL, "
    + "UNIQUE (audio_file_hash, model))"
)
NOTES_SCHEMA = (
    "(id TEXT PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
    + "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, transcription_location TEXT, "
    + "transcription_hash TEXT UNIQUE, note_location TEXT, note_hash TEXT)"
)


def create_db(config: Config):
    if not os.path.isdir(config["db_folder"]):
        os.makedirs(config["db_folder"])
    conn = sqlite3.connect(config["db_path"])
    cur = conn.cursor()
    conn.commit()
    return cur, conn


def setup_db(cur: Cursor, conn: Connection, config: Config):
    _ = cur.execute(f"CREATE TABLE IF NOT EXISTS {config['transcript_db_name']} {TRANSCRIBE_SCHEMA};")
    conn.commit()
    _ = cur.execute(f"CREATE TABLE IF NOT EXISTS {config['notes_db_name']} {NOTES_SCHEMA};")
    conn.commit()
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = res.fetchall()
    assert len(tables) == 2
    assert config["transcript_db_name"] in tables[0]
    assert config["notes_db_name"] in tables[1]


def insert_row(cur: Cursor, conn: Connection, table: str, row: dict[str, str], config: Config):
    if table == config["transcript_db_name"]:
        query = (
            f"INSERT INTO {config['transcript_db_name']} "
            + "(id, created_at, updated_at, audio_file_hash, transcription_location, "
            + f"transcription_hash, model) VALUES ('{uuid.uuid4()}', {int(time.time())}, "
            + f"{int(time.time())}, '{row['audio_file_hash']}', "
            + f"'{row['transcription_location']}', '{row['transcription_hash']}', "
            + f"'{config['transcription_model']}');"
        )
    elif table == config["notes_db_name"]:
        query = (
            f"INSERT INTO {config['notes_db_name']} "
            + "(id, created_at, updated_at, transcription_location, transcription_hash, "
            + f"note_location, note_hash) VALUES ('{uuid.uuid4()}', {int(time.time())}, "
            + f"{int(time.time())}, '{row['transcription_location']}', "
            + f"'{row['transcription_hash']}', '{row['note_location']}', "
            + f"'{row['note_hash']}');"
        )
    else:
        raise ValueError(
            f"Unknown table {table}. Valid tables are: {config['transcript_db_name']} and {config['notes_db_name']}"
        )
    try:
        _ = cur.execute(query)
        assert cur.rowcount == 1
        conn.commit()
    except Exception as e:
        print(
            "Unhandled db exception! Please report it at https://github.com/TheWorldJar/tome/issues",
            e,
        )


class TranscribeRow(TypedDict):
    id: str
    created_at: int
    updated_at: int
    audio_file_hash: str
    transcription_location: str | None
    transcription_hash: str | None


class NoteRow(TypedDict):
    id: str
    created_at: int
    updated_at: int
    transcription_location: str | None
    transcription_hash: str | None
    note_location: str | None
    note_hash: str | None


def get_transcription_by_hash_and_model(cur: Cursor, audio_hash: str, config: Config) -> TranscribeRow | None:
    res = cur.execute(
        f"SELECT * FROM {config['transcript_db_name']} "
        + f"WHERE audio_file_hash = '{audio_hash}' AND model = '{config['transcription_model']}'"
    )
    row = cast(tuple[str, int, int, str, str | None, str | None, str] | None, res.fetchone())
    assert cur.rowcount == -1
    if row is None:
        return None
    transcribe_row: TranscribeRow = {
        "id": row[0],
        "created_at": row[1],
        "updated_at": row[2],
        "audio_file_hash": row[3],
        "transcription_location": row[4],
        "transcription_hash": row[5],
    }
    return transcribe_row


def get_note_by_hash(cur: Cursor, transcription_hash: str, config: Config) -> NoteRow | None:
    res = cur.execute(f"SELECT * FROM {config['notes_db_name']} WHERE transcription_hash = '{transcription_hash}'")
    row = cast(tuple[str, int, int, str | None, str | None, str | None, str | None] | None, res.fetchone())
    assert cur.rowcount == -1
    if row is None:
        return None
    note_row: NoteRow = {
        "id": row[0],
        "created_at": row[1],
        "updated_at": row[2],
        "transcription_location": row[3],
        "transcription_hash": row[4],
        "note_location": row[5],
        "note_hash": row[6],
    }
    return note_row


def update_note(cur: Cursor, conn: Connection, transcription_hash: str, row: dict[str, str], config: Config):
    _ = cur.execute(
        f"UPDATE {config['notes_db_name']} SET updated_at={int(time.time())}, "
        + f"transcription_location='{row['transcription_location']}', "
        + f"note_location='{row['note_location']}', note_hash='{row['note_hash']}' "
        + f"WHERE transcription_hash='{transcription_hash}'"
    )
    assert cur.rowcount == 1
    conn.commit()