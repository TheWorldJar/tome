import os
from typing import cast

from src.tome.config import config_exists, init_config, make_default_config_file
from src.tome.database import (
    create_db,
    get_transcription_by_hash_and_model,
    insert_row,
    setup_db,
)


def test_setup_db():
    if not config_exists():
        make_default_config_file()
    config = init_config()

    if os.path.exists(config["db_path"]):
        os.remove(config["db_path"])

    cur, conn = create_db(config)
    assert cur.rowcount == -1

    setup_db(cur, conn, config)
    assert cur.rowcount == -1
    conn.close()


def test_double_setup_db():
    if not config_exists():
        make_default_config_file()
    config = init_config()

    if os.path.exists(config["db_path"]):
        os.remove(config["db_path"])

    cur, conn = create_db(config)
    assert cur.rowcount == -1

    setup_db(cur, conn, config)
    assert cur.rowcount == -1
    setup_db(cur, conn, config)
    assert cur.rowcount == -1
    conn.close()


def test_db_entry():
    if not config_exists():
        make_default_config_file()
    config = init_config()

    if os.path.exists(config["db_path"]):
        os.remove(config["db_path"])

    cur, conn = create_db(config)
    assert cur.rowcount == -1

    setup_db(cur, conn, config)
    assert cur.rowcount == -1

    test_row = {
        "audio_file_hash": "101-test-101-audio",
        "transcription_location": "./src/tests/transcriptions/test_transcription.txt",
        "transcription_hash": "101-test-101-transcription",
    }

    insert_row(
        cur,
        conn,
        config["transcript_db_name"],
        test_row,
        config,
    )

    row = get_transcription_by_hash_and_model(cur, "101-test-101-audio", config)
    assert row is not None
    assert test_row["audio_file_hash"] in row["audio_file_hash"]
    assert test_row["transcription_location"] in cast(str, row["transcription_location"])
    assert test_row["transcription_hash"] in cast(str, row["transcription_hash"])

    conn.close()


def test_duplicate_db_entry():
    if not config_exists():
        make_default_config_file()
    config = init_config()

    if os.path.exists(config["db_path"]):
        os.remove(config["db_path"])

    cur, conn = create_db(config)
    assert cur.rowcount == -1

    setup_db(cur, conn, config)
    assert cur.rowcount == -1

    test_row = {
        "audio_file_hash": "101-test-101-audio",
        "transcription_location": "./src/tests/transcriptions/test_transcription.txt",
        "transcription_hash": "101-test-101-transcription",
    }

    insert_row(
        cur,
        conn,
        config["transcript_db_name"],
        test_row,
        config,
    )

    row = get_transcription_by_hash_and_model(cur, "101-test-101-audio", config)
    assert row is not None
    assert test_row["audio_file_hash"] in row["audio_file_hash"]
    assert test_row["transcription_location"] in cast(str, row["transcription_location"])
    assert test_row["transcription_hash"] in cast(str, row["transcription_hash"])

    test_row = {
        "audio_file_hash": "101-test-101-audio",
        "transcription_location": "./src/tests/transcriptions/test_transcription.txt",
        "transcription_hash": "101-test-101-transcription",
    }

    insert_row(
        cur,
        conn,
        config["transcript_db_name"],
        test_row,
        config,
    )

    row = get_transcription_by_hash_and_model(cur, "101-test-101-audio", config)
    assert row is not None
    assert test_row["audio_file_hash"] in row["audio_file_hash"]
    assert test_row["transcription_location"] in cast(str, row["transcription_location"])
    assert test_row["transcription_hash"] in cast(str, row["transcription_hash"])

    test_row2 = {
        "audio_file_hash": "101-test-101-audio",
        "transcription_location": "./src/tests/transcriptions/test2_transcription2.md",
        "transcription_hash": "202-test-202-transcription2",
    }
    insert_row(
        cur,
        conn,
        config["transcript_db_name"],
        test_row2,
        config,
    )

    row = get_transcription_by_hash_and_model(cur, "101-test-101-audio", config)
    assert row is not None
    assert test_row["audio_file_hash"] in row["audio_file_hash"]
    assert test_row["transcription_location"] in cast(str, row["transcription_location"])
    assert test_row["transcription_hash"] in cast(str, row["transcription_hash"])

    conn.close()
