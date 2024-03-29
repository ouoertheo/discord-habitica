from typing import Any, Callable
from typing_extensions import SupportsIndex
from loguru import logger
from uuid import uuid4
from dataclasses import dataclass, field
from app.utils import match_all_in_list, ensure_one
from datetime import datetime, timezone
from contextvars import ContextVar

current_transaction_id = ContextVar('transaction',default=None)

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
    exception: Exception = None

@dataclass
class Transaction:
    id: str
    operations: list[Operation] = field(default_factory=list)

class OperationLedger:
    def __init__(self) -> Any:
        self.operations: list[Operation] = []
        self.transactions: dict[str, Transaction] = {}
    
    async def __aenter__(self):
        return await self.start_transaction()

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.end_transaction()
    
    async def start_transaction(self):
        transaction = Transaction(str(uuid4()))
        self.transactions[transaction.id] = transaction

        # Set the contextvar for operations to use
        current_transaction_id.set(transaction.id)
        return transaction

    def end_transaction(self):
        try:
            # Transactions must end with all successful operations
            transaction = self.transactions[current_transaction_id.get()]
            if not all(operation.success for operation in transaction.operations):
                for operation in transaction.operations:
                    # Rollback successful transactions
                    if operation.success:
                        self.rollback(operation)
                        raise TransactionException(f"Not all operations completed. Failed operations: {[op.id for op in transaction.operations if not op.success]}")
        except Exception as e:
            raise TransactionException(f"Error closing transaction {transaction.id} {e}")
    
    def add_operation(self, obj, attr_name, old_value, new_value, rollback_fcn: Callable):
        operation = Operation(str(uuid4()), obj, attr_name, old_value, new_value, created=datetime.now(tz=timezone.utc), rollback_fcn=rollback_fcn)
        self.operations.append(operation)
        transaction_id = current_transaction_id.get()
        if transaction_id:
            self.transactions[transaction_id].operations.append(operation)
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


class TransactableAttribute(int):
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        if not obj:
            return None
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
            if current_transaction_id.get():
                logger.exception(e)
            else:
                raise e


class TransactableInt(int):
    def __new__(cls, value=0):
        obj = super().__new__(cls, value)
        return obj

    def __init__(self, value=0):
        self._original_value = value

    def _handle_exception(self, operation: Operation, e):
        if operation:
            operation.success = False

        # Raise only if not handled in a transaction
        if current_transaction_id.get():
            print("Logging exception:", e)
        else:
            raise e

    def __set__(self, name, value):
        if name == "_original_value":
            super().__setattr__(name, value)
        else:
            operation = None
            try:
                operation = ledger.add_operation(self, self._original_value, value, self.rollback_set)
                super().__setattr__(name, value)
                operation.success = True
            except Exception as e:
                self._handle_exception(operation, e)

    def rollback_set(self, operation: Operation):
        super().__setattr__("_original_value", operation.old_value)


class TransactableList(list):
    def __init__(self, iterable=[]):
        super().__init__(item for item in iterable)
    
    def _handle_exception(self, operation: Operation, e):
        if operation:
            operation.success = False
        
        # Raise only if not handled in a transaction 
        if current_transaction_id.get():
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

class TransactableDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _handle_exception(self, operation: Operation, e):
        if operation:
            operation.success = False

        # Raise only if not handled in a transaction
        if current_transaction_id.get():
            print("Logging exception:", e)
        else:
            raise e

    def __setitem__(self, key, value, ignore=False):
        operation = None
        try:
            if not ignore:
                # Key may not exist
                operation = ledger.add_operation(self, key, self.get(key, None), value, self.rollback_set)
            super().__setitem__(key, value)
            if not ignore:
                operation.success = True
        except Exception as e:
            self._handle_exception(operation, e)

    def __delitem__(self, key, ignore=False):
        operation = None
        try:
            if not ignore:
                # Key must exist
                operation = ledger.add_operation(self, key, self.get(key), None, self.rollback_remove)
            super().__delitem__(key)
            if operation:
                operation.success = True
        except Exception as e:
            self._handle_exception(operation, e)

    def update(self, *args, **kwargs):
        operation = None
        try:
            if not kwargs.get('ignore', False):
                # If 'ignore' is not provided in kwargs, consider it as False
                for key, value in dict(*args, **kwargs).items():
                    # Key may not exist
                    operation = ledger.add_operation(self, key, self.get(key, None), value, self.rollback_set)
            super().update(*args, **kwargs)
            if operation:
                operation.success = True
        except Exception as e:
            self._handle_exception(operation, e)

    def pop(self, key, default=None, ignore=False):
        operation = None
        try:
            if not ignore:
                # Key may not exist (in the case default is set)
                operation = ledger.add_operation(self, key, self.get(key, None), None, self.rollback_remove)
            return super().pop(key, default)
        except Exception as e:
            self._handle_exception(operation, e)

    def rollback_set(self, operation: Operation):
        # Two ways to set, it can create a key or modify existing key
        if operation.old_value == None:
            del self[operation.attr_name]
        else:
            self[operation.attr_name] = operation.old_value

    def rollback_remove(self, operation: Operation):
        if operation.attr_name not in self:
            self[operation.attr_name] = operation.old_value
        else:
            raise Exception(f"Attempted rollback of dict key {operation.attr_name} remove failed because key exists.")