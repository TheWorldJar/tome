import asyncio
import sys
import time
from datetime import timedelta

from halo import Halo

from src.const import DB_PATH, PROMPT_EXTENSIONS
from src.database import create_db, setup_db
from src.fileactions import get_extension
from transcription import transcribe_text, load_model


# TODO: Test with updated PyTorch
async def main():
    try:
        spinner = Halo(text="Processing...", spinner="bouncingBall")

        db_con = create_db(DB_PATH)
        setup_db(db_con)

        if len(sys.argv) != 3:
            raise Exception("Usage: python main.py {audio_file} {prompt_file}")
        audio_file_path = sys.argv[1]
        prompt_file_path = sys.argv[2]
        prompt_extension = get_extension(prompt_file_path)
        if prompt_extension not in PROMPT_EXTENSIONS:
            raise Exception(
                f"Invalid prompt file extension! Got {prompt_extension}. Valid extensions are: {PROMPT_EXTENSIONS}"
            )
        print(f"Transcribing: {audio_file_path}")

        start = time.time()
        spinner.start()
        model = load_model()
        transcription_file_path = await transcribe_text(audio_file_path, model, db_con)
        spinner.succeed("Done!")
        print("Transcription time: " + str(timedelta(seconds=time.time() - start)))

        print(f"Executing prompt: {prompt_file_path}")
        start = time.time()
        spinner.start()
        # TODO: implement executing prompt.
        spinner.succeed("Done!")
        print("Execution time: " + str(timedelta(seconds=time.time() - start)))
        print("All done!")
    except Exception as e:
        print(e)
        sys.exit(1)
    finally:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
