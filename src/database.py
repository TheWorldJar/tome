import os
import sqlite3
import uuid
from datetime import datetime

from src.const import TRANSCRIBE_DB_NAME, NOTES_DB_NAME, DB_FOLDER

TRANSCRIBE_SCHEMA = "(id TEXT PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, audio_file_hash TEXT UNIQUE, transcription_location TEXT, transcription_hash TEXT)"
NOTES_SCHEMA = "(id TEXT PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, transcription_location TEXT, transcription_hash TEXT UNIQUE, note_location TEXT, note_hash TEXT)"


def create_db(db_path):
    if not (os.path.exists(DB_FOLDER)):
        os.mkdir(DB_FOLDER)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    return cur


def setup_db(cur):
    cur.execute(f"CREATE TABLE IF NOT EXISTS {TRANSCRIBE_DB_NAME} {TRANSCRIBE_SCHEMA}")
    cur.execute(f"CREATE TABLE IF NOT EXISTS {NOTES_DB_NAME} {NOTES_SCHEMA}")
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = res.fetchall()
    assert len(tables) == 2
    assert TRANSCRIBE_DB_NAME in tables[0]
    assert NOTES_DB_NAME in tables[1]


def insert_row(cur, table, row):
    if table == TRANSCRIBE_DB_NAME:
        query = f"INSERT INTO {TRANSCRIBE_DB_NAME} values ({uuid.uuid4()}, {int(datetime.now().timestamp())}, {int(datetime.now().timestamp())}, {row['audio_file_hash']}, {row['transcription_location']}, {row['transcription_hash']})"
    elif table == NOTES_DB_NAME:
        query = f"INSERT INTO {NOTES_DB_NAME} values ({uuid.uuid4()}, {int(datetime.now().timestamp())}, {int(datetime.now().timestamp())}, {row['transcription_location']}, {row['transcription_hash']}, {row['note_location']}, {row['note_hash']})"
    else:
        raise Exception(f"Unknown table {table}")
    try:
        cur.execute(query)
    except Exception as e:
        print(e)


def get_transcription_by_hash(cur, audio_hash):
    res = cur.execute(
        f"SELECT * FROM {TRANSCRIBE_DB_NAME} WHERE audio_file_hash = '{audio_hash}'"
    )
    row = res.fetchone()
    if row is None:
        return None
    return row[0]
