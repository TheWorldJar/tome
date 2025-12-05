import sys
import time
import asyncio

from datetime import timedelta
from halo import Halo

from src.const import DB_PATH
from src.database import create_db, setup_db
from transcription import transcribe_text, load_model


async def main():
    try:
        model = load_model()
        spinner = Halo(text="Processing...", spinner="dots")

        db_con = create_db(DB_PATH)
        setup_db(db_con)

        # TODO: check for the correct number of arguments.
        audio_file_path = sys.argv[1]
        prompt_file_path = sys.argv[2]

        print(f"Transcribing: {audio_file_path}")
        start = time.time()
        spinner.start()
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
