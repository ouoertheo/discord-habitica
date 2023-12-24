import abc
from typing import Type
from uuid import uuid4
from enum import Enum
from datetime import datetime
from loguru import logger
from persistence.driver_base_new import PersistenceDriverBase

class TransactionException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TransactableAddException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TransactableRemoveException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Transactable(abc.ABC):

    @abc.abstractmethod
    async def _add(self, **kwargs) -> None:
        ...
    
    @abc.abstractmethod
    async def _remove(self, **kwargs) -> None:
        ...

    async def add(self, **kwargs):
        try:
            await self._add(kwargs)
        except Exception as e:
            raise TransactableAddException(str(e))

    async def remove(self, **kwargs) -> None:
        try:
            await self._remove(kwargs)
        except Exception as e:
            raise TransactableRemoveException(str(e))


class TransactionStatus(Enum):
    CREATED = "Created"
    IN_PROGRESS = "In progress"
    ERROR = "Error"
    CANCELLED = "Cancelled"

class Transaction:
    def __init__(
        self,
        snd_obj: Transactable,
        snd_params: {},
        rcv_obj: Transactable,
        rcv_params: {},
        description: str,
    ) -> None:
        self.id = str(uuid4())
        self.snd_obj = snd_obj
        self.snd_params = snd_params
        self.rcv_obj = rcv_obj
        self.rcv_params = rcv_params
        self.description = description

        self.snd_completed: bool = False,
        self.rcv_completed: bool = False,
        self.status = TransactionStatus.CREATED
        self.created = datetime.now()
        self.completed: datetime = None
        self.exceptions = ""
    
    def dump(self):
        return{
            "id": self.id,
            "params": self.snd_params,
            "description": self.description,
            "snd_completed": self.snd_completed,
            "rcv_completed": self.rcv_completed,
            "status": self.status,
            "created": self.created,
            "completed": self.completed,
            "exceptions": self.exceptions
        },



class TransactorService:
    status = TransactionStatus
    def __init__(self, driver: PersistenceDriverBase) -> None:
        self.driver = driver
        self.store = self.driver.stores.TRANSACTION
        self.active_transactions = []
    
    def create_transaction(self, params: dict,  snd_obj: Transactable, rcv_obj: Transactable, description):
        transaction =  Transaction(params, snd_obj, rcv_obj, description)
        self.active_transactions.append(transaction)
        return transaction

    async def transact(self, transaction: Transaction):
        try:
            transaction.status = TransactionStatus.IN_PROGRESS
            # Remove from sender
            await transaction.snd_obj.remove(transaction.snd_params)
            transaction.snd_completed = True
            # Add to receiver
            await transaction.rcv_obj.add(transaction.rcv_params)
            transaction.rcv_completed = True
        except TransactableAddException as e : 
            ## If sent but not received, return to send
            if not transaction.rcv_completed and transaction.snd_completed:
                await transaction.snd_obj.add(transaction.snd_params)
            transaction.status = self.status.ERROR
        except TransactableRemoveException as e:
            transaction.status = self.status.ERROR
        transaction.completed = datetime.now()
        self.driver.create(self.store, transaction.dump())
        return transaction


