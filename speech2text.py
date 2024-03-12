import config

if config.params["local_whisper_enabled"]:
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

    def delete():
        if ws._instance is not None:
            del ws._instance.transcriptor
            torch.cuda.empty_cache()
            del ws._instance
            ws._instance = None
        return
