import os
from typing import TypedDict, cast

import yaml


class Config(TypedDict):
    transcripts_folder: str
    output_folder: str
    transcription_model: str
    output_model: str
    db_path: str
    db_folder: str
    transcript_db_name: str
    notes_db_name: str
    hash_algorithm: str
    prompt_extensions: list[str]


DB_PATH = "./db/note.db"
DB_FOLDER = "./db/"
TRANSCRIBE_DB_NAME = "transcriptions"
NOTES_DB_NAME = "notes"
DEFAULT_TRANSCRIBE_PATH = "./transcribe/"
DEFAULT_OUTPUT_PATH = "./note/"
DEFAULT_TRANSCRIBE_MODEL = "turbo"
DEFAULT_OUTPUT_MODEL = "gemma3:4b"
HASH_ALGORITHM = "sha256"
PROMPT_EXTENSIONS = [".txt", ".md"]


def config_exists():
    return os.path.exists("./config.yaml") and os.path.isfile("config.yaml")


def make_default_config_file():
    data = {
        "transcripts_folder": DEFAULT_TRANSCRIBE_PATH,
        "output_folder": DEFAULT_OUTPUT_PATH,
        "transcription_model": DEFAULT_TRANSCRIBE_MODEL,
        "output_model": DEFAULT_OUTPUT_MODEL,
    }
    with open("config.yaml", "w") as f:
        yaml.dump(data, f)


def init_config() -> Config:
    config: Config = {
        "transcripts_folder": DEFAULT_TRANSCRIBE_PATH,
        "output_folder": DEFAULT_OUTPUT_PATH,
        "transcription_model": DEFAULT_TRANSCRIBE_MODEL,
        "output_model": DEFAULT_OUTPUT_MODEL,
        "db_path": DB_PATH,
        "db_folder": DB_FOLDER,
        "transcript_db_name": TRANSCRIBE_DB_NAME,
        "notes_db_name": NOTES_DB_NAME,
        "hash_algorithm": HASH_ALGORITHM,
        "prompt_extensions": PROMPT_EXTENSIONS,
    }
    with open("config.yaml", "r") as f:
        data: dict[str, str] = cast(dict[str, str], yaml.safe_load(f))
    if (
        "transcription_model" not in data
        or "output_model" not in data
        or "transcripts_folder" not in data
        or "output_folder" not in data
    ):
        print("Invalid configuration. Loading default config.")
        make_default_config_file()
    else:
        config["transcripts_folder"] = data["transcripts_folder"]
        config["output_folder"] = data["output_folder"]
        config["transcription_model"] = data["transcription_model"]
        config["output_model"] = data["output_model"]
    return config
