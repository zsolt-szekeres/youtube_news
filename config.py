import json
import os


class _ConfigParser:
    def __init__(self, config_file):
        with open(config_file, "r") as f:
            self.data = json.load(f)

    @property
    def youtube_channels(self):
        return self.data["youtube_channels"]

    @property
    def gpt(self):
        return self.data["gpt"]

    @property
    def chunking_parameters(self):
        return self.data["chunking"]

    @property
    def lookback_days(self):
        return self.data["lookback_days"]

    @property
    def run_mode(self):
        return self.data["run_mode"]

    @property
    def backup_folder(self):
        return self.data["backup_folder"]

    @property
    def vector_store(self):
        return self.data["vector_store"]

    @property
    def videos_folder(self):
        return self.data["videos_folder"]

    @property
    def log_folder(self):
        return self.data["log_folder"]

    @property
    def auth_codes(self):
        auth_codes = {}
        for key, env_var in self.data["auth_codes_env_vars"].items():
            auth_codes[key] = os.environ.get(env_var)
        return auth_codes

    @property
    def email(self):
        if self.data["run_mode"] == "DEBUG":
            self.data["email"]["receiver_emails"] = [self.data["email"]["sender_email"]]
        return self.data["email"]

    @property
    def yt_transcript_api_enabled(self):
        return self.data["yt_transcript_api_enabled"]

    @property
    def local_whisper_enabled(self):
        return self.data["local_whisper_enabled"]

    @property
    def force_download_audio(self):
        return self.data["force_download_audio"]


_config_parser = _ConfigParser("config.json")
params = {
    "youtube_channels": _config_parser.youtube_channels,
    "gpt": _config_parser.gpt,
    "chunking": _config_parser.chunking_parameters,
    "lookback_days": _config_parser.lookback_days,
    "auth_codes": _config_parser.auth_codes,
    "email": _config_parser.email,
    "run_mode": _config_parser.run_mode,
    "log_folder": _config_parser.log_folder,
    "videos_folder": _config_parser.videos_folder,
    "backup_folder": _config_parser.backup_folder,
    "vector_store": _config_parser.vector_store,
    "yt_transcript_api_enabled": _config_parser.yt_transcript_api_enabled,
    "local_whisper_enabled": _config_parser.local_whisper_enabled,
    "force_download_audio": _config_parser.force_download_audio,
}
