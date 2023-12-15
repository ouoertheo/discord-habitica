import abc
from enum import StrEnum

# Any app specific stores are passed using this enum. Implementations should create stores using this.
class StoreType(StrEnum):
    APP_USER = "app_user"
    BANK = "bank"
    BANK_USER = "bank_user"
    BANK_ACCOUNT = "bank_account"
    TRANSACTION = "transaction"

class PersistenceDriverBase(metaclass=abc.ABCMeta):
    stores = StoreType
    store_cache: dict
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def list(self, store) -> dict:
        pass

    @abc.abstractmethod
    def create(self, store, data) -> dict:
        pass

    @abc.abstractmethod
    def read(self, store, id) -> dict:
        pass
    
    @abc.abstractmethod
    def update(self, store, data) -> dict:
        pass

    @abc.abstractmethod
    def delete(self, store, id) -> None:
        pass
