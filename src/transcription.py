import whisper

from src.fileactions import write_file

def load_model():
    model = whisper.load_model("medium.en")
    return model

def transcribe(location, model):
    result = model.transcribe(location)
    write_file(result)
    del model