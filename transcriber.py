from pydub import AudioSegment
import whisper
import tempfile


def load_model(model_type):
    model = whisper.load_model(model_type)
    return model

class Transcriber:
    def __init__(self, model_type) -> None:
        self.model = load_model(model_type)
    
    def convert_m4a_to_wav(self, file_path):
        if not file_path.endswith(".m4a"):
            raise ValueError("Invalid file type. Only .m4a files are supported.")
        audio_file = AudioSegment.from_file(file_path, format="m4a")
        audio_file = audio_file.set_frame_rate(16000)
        temp = tempfile.NamedTemporaryFile(suffix=".wav")
        audio_file.export(temp.name, format="wav")
        return temp
    
    def transcribe(self, file_path):
        file = self.convert_m4a_to_wav(file_path)
        transcript = self.model.transcribe(file.name)
        return transcript['text']

if __name__ == "__main__":
    t = Transcriber("base.en")
    print(t.transcribe("test.m4a"))