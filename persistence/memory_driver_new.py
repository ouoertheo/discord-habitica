from persistence.driver_base_new import PersistenceDriverBase

class PersistenceMemoryDriver(PersistenceDriverBase):
    def __init__(self) -> None:
        # Init empty store for each store type in PersistenceDriverBase class
        self.store_cache = {
            store.value:{}
            for store in self.stores
        }

    def list(self, store):
        return self.store_cache[store]

    def create(self, store, model):
        return self.update(store, model)

    def read(self, store, id):
        return self.store_cache[store][id]
    
    def update(self, store, model):
        self.store_cache[store][model['id']] = model

    def delete(self, store,  id):
        del self.store_cache[store][id]