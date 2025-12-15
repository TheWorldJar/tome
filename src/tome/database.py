import os
import sqlite3
import time
import uuid

TRANSCRIBE_SCHEMA = "(id TEXT PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, audio_file_hash TEXT NOT NULL, transcription_location TEXT, transcription_hash TEXT, model TEXT NOT NULL, UNIQUE (audio_file_hash, model))"
NOTES_SCHEMA = "(id TEXT PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, transcription_location TEXT, transcription_hash TEXT UNIQUE, note_location TEXT, note_hash TEXT)"


def create_db(config):
    if not os.path.isdir(config["DB_FOLDER"]):
        os.makedirs(config["DB_FOLDER"])
    conn = sqlite3.connect(config["DB_PATH"])
    cur = conn.cursor()
    conn.commit()
    return cur, conn


def setup_db(cur, conn, config):
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS {config['TRANSCRIBE_DB_NAME']} {TRANSCRIBE_SCHEMA};"
    )
    conn.commit()
    cur.execute(f"CREATE TABLE IF NOT EXISTS {config['NOTES_DB_NAME']} {NOTES_SCHEMA};")
    conn.commit()
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = res.fetchall()
    assert len(tables) == 2
    assert config["TRANSCRIBE_DB_NAME"] in tables[0]
    assert config["NOTES_DB_NAME"] in tables[1]


def insert_row(cur, conn, table, row, config):
    if table == config["TRANSCRIBE_DB_NAME"]:
        query = f"INSERT INTO {config['TRANSCRIBE_DB_NAME']} (id, created_at, updated_at, audio_file_hash, transcription_location, transcription_hash, model) VALUES ('{uuid.uuid4()}', {int(time.time())}, {int(time.time())}, '{row['audio_file_hash']}', '{row['transcription_location']}', '{row['transcription_hash']}', '{config['transcription_model']}');"
    elif table == config["NOTES_DB_NAME"]:
        query = f"INSERT INTO {config['NOTES_DB_NAME']} (id, created_at, updated_at, transcription_location, transcription_hash, note_location, note_hash) VALUES ('{uuid.uuid4()}', {int(time.time())}, {int(time.time())}, '{row['transcription_location']}', '{row['transcription_hash']}', '{row['note_location']}', '{row['note_hash']}');"
    else:
        raise Exception(f"Unknown table {table}")
    try:
        cur.execute(query)
        assert cur.rowcount == 1
        conn.commit()
    except Exception as e:
        print(
            "Unhandled db exception! Please report it at https://github.com/TheWorldJar/tome/issues",
            e,
        )


def get_transcription_by_hash_and_model(cur, audio_hash, config):
    res = cur.execute(
        f"SELECT * FROM {config['TRANSCRIBE_DB_NAME']} WHERE audio_file_hash = '{audio_hash}' AND model = '{config['transcription_model']}'"
    )
    row = res.fetchone()
    assert cur.rowcount == -1
    if row is None:
        return None
    transcribe_row = {
        "id": row[0],
        "created_at": row[1],
        "updated_at": row[2],
        "audio_file_hash": row[3],
        "transcription_location": row[4],
        "transcription_hash": row[5],
    }
    return transcribe_row


def get_note_by_hash(cur, transcription_hash, config):
    res = cur.execute(
        f"SELECT * FROM {config['NOTES_DB_NAME']} WHERE transcription_hash = '{transcription_hash}'"
    )
    row = res.fetchone()
    assert cur.rowcount == -1
    if row is None:
        return None
    note_row = {
        "id": row[0],
        "created_at": row[1],
        "updated_at": row[2],
        "transcription_location": row[3],
        "transcription_hash": row[4],
        "note_location": row[5],
        "note_hash": row[6],
    }
    return note_row


def update_note(cur, conn, transcription_hash, row, config):
    cur.execute(
        f"UPDATE {config['NOTES_DB_NAME']} SET updated_at={int(time.time())}, transcription_location='{row['transcription_location']}', note_location='{row['note_location']}', note_hash='{row['note_hash']}' WHERE transcription_hash='{transcription_hash}'"
    )
    assert cur.rowcount == 1
    conn.commit()
