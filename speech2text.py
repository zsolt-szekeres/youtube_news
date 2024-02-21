import whisper
import torch


class ws:
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Make sure it's a singleton to protect GPU memory
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.transcriptor = whisper.load_model("medium")
        return cls._instance

    def transcribe(self, fullname):
        transcript = self.transcriptor.transcribe(fullname)
        torch.cuda.empty_cache()
        return transcript
