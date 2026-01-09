import gc
import sys
import time
from datetime import timedelta

import torch
from halo import Halo

from .config import (
    config_exists,
    init_config,
    make_default_config_file,
)
from .database import create_db, setup_db
from .execution import get_ollama_response
from .fileactions import get_extension
from .transcription import load_model, transcribe_text


def main():
    try:
        torch.cuda.empty_cache()
        spinner = Halo(text="This may take a while...", spinner="bouncingBall")

        if not config_exists():
            make_default_config_file()
        config = init_config()

        db_cur, db_conn = create_db(config)
        setup_db(db_cur, db_conn, config)

        if len(sys.argv) != 3:
            raise Exception("Usage: tome {audio_file} {prompt_file}")
        audio_file_path = sys.argv[1]
        prompt_file_path = sys.argv[2]
        prompt_extension = get_extension(prompt_file_path)
        if prompt_extension not in config["prompt_extensions"]:
            raise Exception(
                f"Invalid prompt file extension! Got {prompt_extension}. Valid extensions are: {config['prompt_extensions']}"
            )
        print(f"Transcribing: {audio_file_path}")

        start = time.time()
        _ = spinner.start()
        model = load_model(config)
        transcription_file_path, file_id = transcribe_text(
            audio_file_path,
            model,
            db_cur,
            db_conn,
            config,
        )
        _ = spinner.succeed("Done!")
        print("Transcription time: " + str(timedelta(seconds=time.time() - start)))
        del model
        torch.cuda.empty_cache()
        _ = gc.collect()

        print(f"Executing prompt: {prompt_file_path}")
        start = time.time()
        _ = spinner.start()
        note_location = get_ollama_response(
            db_cur,
            db_conn,
            transcription_file_path,
            prompt_file_path,
            file_id,
            config,
        )
        _ = spinner.succeed("Done!")
        print("Execution time: " + str(timedelta(seconds=time.time() - start)))
        print(f"All done! You note is available at: {note_location}")
        db_cur.close()
        db_conn.close()
    except FileNotFoundError | ValueError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(
            "Unhandled exception! Please report it at https://github.com/TheWorldJar/tome/issues",
            e,
        )
        sys.exit(1)
    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()
