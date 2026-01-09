import hashlib
import os
from datetime import timedelta
from typing import TypedDict
from uuid import UUID

from .config import Config


class Segment(TypedDict):
    start: float
    end: float
    text: str


def write_transcript(transcription: dict[str, list[Segment]], file_id: UUID, config: Config):
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
    if not os.path.exists(config["transcripts_folder"]) or not os.path.isdir(config["transcripts_folder"]):
        os.makedirs(config["transcripts_folder"])
    location = os.path.join(config["transcripts_folder"], str(file_id)) + ".txt"
    with open(location, "w", encoding="utf-8") as f:
        _ = f.write(text)
    return location


def get_file_hash(file_path: str, config: Config):
    hash_func = hashlib.new(config["hash_algorithm"])
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def get_extension(file_path: str):
    return os.path.splitext(file_path)[1]


def read_file(file_path: str):
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()
    if len(data) == 0:
        raise ValueError(f"Aborting execution! File content is empty for {file_path}")
    return data


def write_note(note: str, file_id: UUID, config: Config):
    if not os.path.exists(config["output_folder"]) or not os.path.isdir(config["output_folder"]):
        os.makedirs(config["output_folder"])

    location = os.path.join(config["output_folder"], str(file_id)) + ".txt"
    with open(location, "w", encoding="utf-8") as f:
        _ = f.write(note)
    return location
