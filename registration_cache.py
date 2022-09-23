
import json
import os
import dotenv
import config as cfg

dotenv.load_dotenv()

STORE_DIR = os.getenv("STORE_DIR")
REGISTRATION_CACHE = f"./{STORE_DIR}/registration_cache.json"



class RegistrationCache:
    cache = {}
    def __init__(self) -> None:
        self.verify_files()
        self.read_cache()

    def verify_files(self):
        "Make sure the cache files exists"
        if not os.path.exists(REGISTRATION_CACHE):
            with open(REGISTRATION_CACHE, 'x') as fh:
                json.dump({}, fh)

    def read_cache(self):
        with open(REGISTRATION_CACHE, 'r') as fh:
            self.cache = json.load(fh)
    
    def write_cache(self):
        with open(REGISTRATION_CACHE,'w') as fh:
            json.dump(self.cache, fh)

    def save_channel(self, channel_id, group_id):
        self.cache[group_id] = channel_id
        self.write_cache()

    def get_channel(self,group_id) -> str:
        """
        Returns: channel_id
        Exception: KeyError
        """
        self.read_cache()
        return self.cache[group_id]
    
    def is_channel_registered(self, channel_id):
        self.read_cache()
        return bool([c for c in self.cache if self.cache[c] == channel_id])

