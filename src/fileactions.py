import hashlib
import os
import uuid
from datetime import timedelta

from src.const import TRANSCRIBE_PATH, HASH_ALGORITHM


def write_transcript(transcription):
    segments = transcription["segments"]
    text = ""
    for segment in segments:
        text += (
            str(timedelta(seconds=segment["start"]))
            + " - "
            + str(timedelta(seconds=segment["end"]))
            + " : "
            + segment["text"].strip()
            + "\n"
        )
    if not os.path.exists(TRANSCRIBE_PATH) or not os.path.isdir(TRANSCRIBE_PATH):
        os.makedirs(TRANSCRIBE_PATH)
    location = f"{TRANSCRIBE_PATH}{uuid.uuid4()}"
    with open(location, "w", encoding="utf-8") as f:
        f.write(text)
    return location


def get_file_hash(file_path):
    hash_func = hashlib.new(HASH_ALGORITHM)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def get_extension(file_path):
    return os.path.splitext(file_path)[1]
