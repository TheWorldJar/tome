import sys

from transcription import transcribe, load_model

if __name__ == '__main__':
    try:
        model = load_model()
        location = sys.argv[1]
        print(f'Transcribing {location}')
        transcribe(location, model)
    except Exception as e:
        print(e)
        del model
        sys.exit(1)
    finally:
        del model
        sys.exit(0)