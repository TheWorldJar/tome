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
from .transcription import load_model, start_transcription


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
            raise ValueError("Usage: tome {audio_file} {prompt_file}")
        if not isinstance(args.audio_file, str):
            raise ValueError("Make sure to provide a valid audio file path in between quotes!")
        if not isinstance(args.prompt_file, str):
            raise ValueError("Make sure to provide a valid prompt file path in between quotes!")

        prompt_extension = get_extension(args.prompt_file)
        if prompt_extension not in config["prompt_extensions"]:
            raise ValueError(
                f"Invalid prompt file extension! Got {prompt_extension}. Valid extensions are: {config['prompt_extensions']}"
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
                "\n\nCUDA out of memory! Please change the transcription_model in config.yaml to a smaller model"
                + f"\nCurrent transcription_model: {config['transcription_model']}"
                + f"\nDefault transcription_model: {DEFAULT_TRANSCRIBE_MODEL}"
                + "If that did not help, please report it at https://github.com/TheWorldJar/tome/issues"
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
                "\n\nCUDA out of memory! Please change the output_model and/or context_size in config.yaml to a smaller model."
                + f"\nCurrent output_model: {config['output_model']}"
                + f"\nCurrent context_size: {config['context_size']}"
                + f"\nDefault output_model: {DEFAULT_OUTPUT_MODEL}"
                + f"\nDefault context_size: {CONTEXT_SIZE}"
                + "If that did not help, please report it at https://github.com/TheWorldJar/tome/issues"
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
            "\n\nUnhandled CUDA out of memory error! Please report it at https://github.com/TheWorldJar/tome/issues\n\n",
            e,
        )
        sys.exit(1)
    except Exception as e:
        print(
            "\n\nUnhandled exception! Please report it at https://github.com/TheWorldJar/tome/issues\n\n",
            e,
            "\n\nType: ",
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
