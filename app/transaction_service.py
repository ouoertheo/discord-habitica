import asyncio
from typing import Any, Callable
from typing_extensions import SupportsIndex
from loguru import logger
from uuid import uuid4
from dataclasses import dataclass, field
from app.utils import match_all_in_list, ensure_one
from datetime import datetime, timezone
import contextvars
from functools import wraps

class RollbackException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TransactionException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

@dataclass
class Operation:
    id: str
    obj: object
    attr_name: Any
    old_value: Any
    new_value: Any
    created: datetime
    rollback_fcn: Callable = None
    success: bool = False

@dataclass
class Transaction:
    id: str
    operations: list[Operation] = field(default_factory=list)

class OperationLedger:
    def __init__(self) -> Any:
        self.operations: list[Operation] = []
        self.transactions: dict[str, Transaction] = {}
        self.current_transaction: Transaction = None
        self.transaction_lock = asyncio.Lock()
    
    async def __aenter__(self):
        return await self.start_transaction()

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.end_transaction()
    
    async def start_transaction(self):
        await self.transaction_lock.acquire()
        try:
            transaction = Transaction(id = str(uuid4()))
            self.transactions[transaction.id] = transaction
            self.current_transaction = transaction
            return transaction
        except Exception as e:
            self.transaction_lock.release()
            self.current_transaction = None
            t = transaction.id if transaction else None
            raise TransactionException(f"Error starting transaction {t} {e}")

    def end_transaction(self):
        try:
            if not all(operation.success for operation in self.current_transaction.operations):
                for operation in self.current_transaction.operations:
                    if operation.success:
                        self.rollback(operation)
                        raise TransactionException(f"Not all operations completed. Failed operations: {[op.id for op in self.current_transaction.operations if not op.success]}")
        except TransactionException as e:
            raise TransactionException(f"Error closing transaction {self.current_transaction.id} {e}")
        finally:
            self.transaction_lock.release()
            self.current_transaction = None
    
    def add_operation(self, obj, attr_name, old_value, new_value, rollback_fcn: Callable):
        operation = Operation(str(uuid4()), obj, attr_name, old_value, new_value, created=datetime.now(tz=timezone.utc), rollback_fcn=rollback_fcn)
        self.operations.append(operation)
        if self.current_transaction:
            self.current_transaction.operations.append(operation)
        return operation
    
    @ensure_one
    def get_operation(self, obj=None, attr_name="", old_value=None, new_value=None):
        return match_all_in_list(
            self.operations,
            obj=obj,
            attr_name=attr_name,
            old_value=old_value,
            new_value=new_value
        )
    
    def rollback(self, operation: Operation):
        try:
            if operation.rollback_fcn:
                operation.rollback_fcn(operation)
            else:
                setattr(operation.obj, operation.attr_name, operation.old_value)
        except Exception as e:
            raise RollbackException(f"Rollback of operation {operation} failed. Exception: {str(e)}")

ledger = OperationLedger()


class TransactableAttribute:
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        value = getattr(obj, self.private_name)
        return value

    def __set__(self, obj, value):
        try:
            operation = None
            self.obj = obj
            if self.private_name in vars(obj):
                operation = ledger.add_operation(obj, self.private_name, vars(obj)[self.private_name], value, None)
            setattr(obj, self.private_name, value)
            
            if operation:
                operation.success = True
        except Exception as e:
            if operation:
                operation.success = False
            
            # Raise only if not handled in a transaction 
            if ledger.current_transaction:
                logger.exception(e)
            else:
                raise e

class TransactableList(list):
    def __init__(self, iterable=[]):
        super().__init__(item for item in iterable)
    
    def _handle_exception(self, operation: Operation, e):
        if operation:
            operation.success = False
        
        # Raise only if not handled in a transaction 
        if ledger.current_transaction:
            logger.exception(e)
        else:
            raise e
    
    def __setitem__(self, index, item, ignore=False):
        operation = None
        try:
            if not ignore:
                operation = ledger.add_operation(self, index, self[index], item, self.rollback_set)
            super().__setitem__(index, item)
            if not ignore:
                operation.success = True
        except Exception as e:
            self._handle_exception(operation, e)

    def insert(self, index: SupportsIndex, item: Any, ignore=False) -> None:
        operation = None
        try:
            if not ignore:
                operation = ledger.add_operation(self, index, None, item, self.rollback_add)
            super().insert(index, item) 
            if operation:
                operation.success = True
        except Exception as e:
            self._handle_exception(operation, e)
    
    def append(self, item, ignore=False):
        operation = None
        try:
            if not ignore:
                operation = ledger.add_operation(self, len(self)-1, None, item, self.rollback_add)
            super().append(item)
            if operation:
                operation.success = True
        except Exception as e:
            self._handle_exception(operation, e)
    
    def remove(self, item, ignore=False) -> None:
        operation = None
        try:
            if not ignore:
                index = self.index(item) if item in self else None
                this_item = self[index] if not index == None else None
                operation = ledger.add_operation(self, index, this_item, None, self.rollback_remove)
            super().remove(item)
            if operation:
                operation.success = True
        except Exception as e:
            self._handle_exception(operation, e)

    def rollback_add(self, operation: Operation):
        self.remove(operation.new_value, ignore=True)
    
    def rollback_remove(self, operation: Operation):
        self.insert(operation.attr_name, operation.old_value, ignore=True)
    
    def rollback_set(self, operation: Operation):
        index = self.index(operation.new_value)
        self[index] = operation.old_value
        


class Person:

    age = TransactableAttribute()             # Descriptor instance

    def __init__(self, name, age):
        self.name = name                # Regular instance attribute
        self.age = age                  # Calls __set__()

    def birthday(self):
        self.age += 1                   # Calls both __get__() and __set__()

