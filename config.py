import json
import os

class _ConfigParser:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.data = json.load(f)
    
    @property
    def youtube_channels(self):
        return self.data['youtube_channels']
    
    @property
    def gpt_prompts(self):
        return self.data['gpt_prompts']
    
    @property
    def chunking_parameters(self):
        return self.data['chunking']
    
    @property
    def lookback_days(self):
        return self.data['lookback_days']
    
    @property
    def auth_codes(self):
        auth_codes = {}
        for key, env_var in self.data['auth_codes_env_vars'].items():
            auth_codes[key] = os.environ.get(env_var)
        return auth_codes
    
    @property
    def email(self):
        return self.data['email']

_config_parser = _ConfigParser('config.json')
params = {
    "youtube_channels": _config_parser.youtube_channels,
    "gpt_prompts": _config_parser.gpt_prompts,
    "chunking": _config_parser.chunking_parameters,
    "lookback_days": _config_parser.lookback_days,
    "auth_codes": _config_parser.auth_codes,
    "email": _config_parser.email
}