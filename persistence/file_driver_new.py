import json
import os
from pathlib import Path
from persistence.driver_base_new import PersistenceDriverBase

class PersistenceFileDriver(PersistenceDriverBase):
    def __init__(self, base_dir: str) -> None:
            
        self.base_dir = Path(base_dir)
        if not self.base_dir.exists():
            self.base_dir.mkdir()

        # Init empty store for each store type in PersistenceDriverBase class
        self.store_cache: dict[str, Path] = {
            store.value:self.base_dir.joinpath(f"{store.value}.json")
            for store in self.stores
        }
        self.verify_files()
    
    def _load_store(self, store):
        with open(self.store_cache[store],"r") as store:
            return json.load(store)
    
    def _dump_store(self, store, payload: dict):
        with open(self.store_cache[store],"w") as store:
            json.dump(payload, store)
    
    def verify_files(self):
        "Make sure the persistence files exists"
        for store_path in self.store_cache.values():
            if not store_path.exists():
                with store_path.open('w') as fh:
                    json.dump({}, fh)
    
    def list(self, store):
        return self._load_store(store)

    def create(self, store, data):
        objects: dict = self._load_store(store)
        objects[data['id']] = data
        self._dump_store(store, objects)

    def read(self, store, id):
        objects: dict = self._load_store(store)
        return objects[id]
    
    def update(self, store, data):
        objects: dict = self._load_store(store)
        objects[data['id']] = data
        self._dump_store(store,objects)

    def delete(self, store, id):
        objects: dict = self._load_store(store)
        del objects[id]
        self._dump_store(store,objects)