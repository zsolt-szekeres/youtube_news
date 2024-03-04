import config

if not config.params["yt_transcript_api_enabled"]:
    import whisper
    import torch


class ws:
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Make sure it's a singleton to protect GPU memory
        if not cls._instance and not config.params["yt_transcript_api_enabled"]:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.transcriptor = whisper.load_model("medium")
        return cls._instance

    def transcribe(self, fullname):
        if config.params["yt_transcript_api_enabled"]:
            return None
        transcript = self.transcriptor.transcribe(fullname)
        torch.cuda.empty_cache()
        return transcript
