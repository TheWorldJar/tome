import os

from src.const import DB_PATH, TRANSCRIBE_DB_NAME
from src.database import create_db, setup_db, insert_row, get_transcription_by_hash


def test_setup_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    cur, conn = create_db(DB_PATH)
    assert cur.rowcount == -1

    setup_db(cur, conn)
    assert cur.rowcount == -1
    conn.close()


def test_double_setup_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    cur, conn = create_db(DB_PATH)
    assert cur.rowcount == -1

    setup_db(cur, conn)
    assert cur.rowcount == -1
    setup_db(cur, conn)
    assert cur.rowcount == -1
    conn.close()


def test_db_entry():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    cur, conn = create_db(DB_PATH)
    assert cur.rowcount == -1

    setup_db(cur, conn)
    assert cur.rowcount == -1

    test_row = {
        "audio_file_hash": "101-test-101-audio",
        "transcription_location": "./src/tests/transcriptions/test_transcription.txt",
        "transcription_hash": "101-test-101-transcription",
    }

    insert_row(
        cur,
        conn,
        TRANSCRIBE_DB_NAME,
        test_row,
    )

    row = get_transcription_by_hash(cur, "101-test-101-audio")
    assert row is not None
    assert test_row["audio_file_hash"] in row["audio_file_hash"]
    assert test_row["transcription_location"] in row["transcription_location"]
    assert test_row["transcription_hash"] in row["transcription_hash"]

    conn.close()


def test_duplicate_db_entry():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    cur, conn = create_db(DB_PATH)
    assert cur.rowcount == -1

    setup_db(cur, conn)
    assert cur.rowcount == -1

    test_row = {
        "audio_file_hash": "101-test-101-audio",
        "transcription_location": "./src/tests/transcriptions/test_transcription.txt",
        "transcription_hash": "101-test-101-transcription",
    }

    insert_row(
        cur,
        conn,
        TRANSCRIBE_DB_NAME,
        test_row,
    )

    row = get_transcription_by_hash(cur, "101-test-101-audio")
    assert row is not None
    assert test_row["audio_file_hash"] in row["audio_file_hash"]
    assert test_row["transcription_location"] in row["transcription_location"]
    assert test_row["transcription_hash"] in row["transcription_hash"]

    test_row = {
        "audio_file_hash": "101-test-101-audio",
        "transcription_location": "./src/tests/transcriptions/test_transcription.txt",
        "transcription_hash": "101-test-101-transcription",
    }

    insert_row(
        cur,
        conn,
        TRANSCRIBE_DB_NAME,
        test_row,
    )

    row = get_transcription_by_hash(cur, "101-test-101-audio")
    assert row is not None
    assert test_row["audio_file_hash"] in row["audio_file_hash"]
    assert test_row["transcription_location"] in row["transcription_location"]
    assert test_row["transcription_hash"] in row["transcription_hash"]

    test_row2 = {
        "audio_file_hash": "101-test-101-audio",
        "transcription_location": "./src/tests/transcriptions/test2_transcription2.md",
        "transcription_hash": "202-test-202-transcription2",
    }
    insert_row(
        cur,
        conn,
        TRANSCRIBE_DB_NAME,
        test_row2,
    )

    row = get_transcription_by_hash(cur, "101-test-101-audio")
    assert row is not None
    assert test_row["audio_file_hash"] in row["audio_file_hash"]
    assert test_row["transcription_location"] in row["transcription_location"]
    assert test_row["transcription_hash"] in row["transcription_hash"]

    conn.close()
