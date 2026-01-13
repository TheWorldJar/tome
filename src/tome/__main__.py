import argparse
import gc
import sys
import time
from datetime import timedelta

import torch
from halo import Halo

from .config import (
    CONTEXT_SIZE,
    DEFAULT_OUTPUT_MODEL,
    DEFAULT_TRANSCRIBE_MODEL,
    config_exists,
    init_config,
    make_default_config_file,
)
from .database import create_db, setup_db
from .execution import get_ollama_response
from .fileactions import get_extension
from .messages import (
    CUDA_OOM_EXECUTION_TEMPLATE,
    CUDA_OOM_TRANSCRIPTION_TEMPLATE,
    EXCEPTION_TYPE_PREFIX,
    INVALID_AUDIO_FILE_PATH,
    INVALID_PROMPT_EXTENSION_TEMPLATE,
    INVALID_PROMPT_FILE_PATH,
    UNHANDLED_CUDA_OOM_ERROR,
    UNHANDLED_EXCEPTION_ERROR,
    USAGE_ERROR,
)
from .transcription import load_model, start_transcription

# TODO: Find some way to validate the setup script.
# TODO: Get a Windows setup script.


def main():
    db_cur = None
    db_conn = None
    try:
        parser = argparse.ArgumentParser(description="Transcribe audio files and generate notes using LLM prompts")
        _ = parser.add_argument(
            "audio_file",
            type=str,
            help="Path to the audio file to transcribe",
        )
        _ = parser.add_argument(
            "prompt_file",
            type=str,
            help="Path to the prompt file to use for note generation",
        )

        args = parser.parse_args()
        torch.cuda.empty_cache()
        spinner = Halo(text="This may take a while...", spinner="bouncingBall")

        if not config_exists():
            make_default_config_file()
        config = init_config()

        db_cur, db_conn = create_db(config)
        setup_db(db_cur, db_conn, config)

        if args.audio_file is None or args.prompt_file is None:
            raise ValueError(USAGE_ERROR)
        if not isinstance(args.audio_file, str):
            raise ValueError(INVALID_AUDIO_FILE_PATH)
        if not isinstance(args.prompt_file, str):
            raise ValueError(INVALID_PROMPT_FILE_PATH)

        prompt_extension = get_extension(args.prompt_file)
        if prompt_extension not in config["prompt_extensions"]:
            raise ValueError(
                INVALID_PROMPT_EXTENSION_TEMPLATE.format(
                    prompt_extension=prompt_extension,
                    valid_extensions=config["prompt_extensions"],
                )
            )
        print(f"Transcribing: {args.audio_file}")

        start = time.time()
        _ = spinner.start()
        try:
            model = load_model(config)
            transcription_file_path, file_id = start_transcription(
                args.audio_file,
                model,
                db_cur,
                db_conn,
                config,
            )
        except torch.OutOfMemoryError:
            raise ValueError(
                CUDA_OOM_TRANSCRIPTION_TEMPLATE.format(
                    current_model=config["transcription_model"],
                    default_model=DEFAULT_TRANSCRIBE_MODEL,
                )
            )

        _ = spinner.succeed("Done!")
        print("Transcription time: " + str(timedelta(seconds=time.time() - start)))
        del model
        torch.cuda.empty_cache()
        _ = gc.collect()

        print(f"Executing prompt: {args.prompt_file}")
        start = time.time()
        _ = spinner.start()

        try:
            note_location = get_ollama_response(
                db_cur,
                db_conn,
                transcription_file_path,
                args.prompt_file,
                file_id,
                config,
            )
        except torch.OutOfMemoryError:
            raise ValueError(
                CUDA_OOM_EXECUTION_TEMPLATE.format(
                    current_output_model=config["output_model"],
                    current_context_size=config["context_size"],
                    default_output_model=DEFAULT_OUTPUT_MODEL,
                    default_context_size=CONTEXT_SIZE,
                )
            )

        _ = spinner.succeed("Done!")
        print("Execution time: " + str(timedelta(seconds=time.time() - start)))
        print(f"All done! Your note is available at: {note_location}")
        db_cur.close()
        db_conn.close()
    except (FileNotFoundError, ValueError) as e:
        print("\n\n", e)
        sys.exit(1)
    except torch.OutOfMemoryError as e:
        print(
            UNHANDLED_CUDA_OOM_ERROR,
            e,
        )
        sys.exit(1)
    except Exception as e:
        print(
            UNHANDLED_EXCEPTION_ERROR,
            e,
            EXCEPTION_TYPE_PREFIX,
            type(e),
        )
        sys.exit(1)
    finally:
        if db_cur is not None:
            try:
                db_cur.close()
            except Exception:
                pass
        if db_conn is not None:
            try:
                db_conn.close()
            except Exception:
                pass
        torch.cuda.empty_cache()
        _ = gc.collect()


if __name__ == "__main__":
    main()
