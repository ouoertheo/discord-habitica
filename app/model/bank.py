# Habitica Bank
from dataclasses import dataclass, asdict, field
from typing import Optional
from enum import Enum
import dacite
from uuid import uuid4

@dataclass
class BankLoanAccount:
    """
    Create a loan account.
    name: The name of the account
    app_user_id: the Habitica App User that owns the account
    """
    id: str
    name: str
    bank_id: str
    app_user_id: str
    habitica_user_id: str
    amount: float
    interest: float
    term: int
    principal: float
    balance: float = 0
    account_type = "BankLoanAccount"

@dataclass
class BankAccount:
    id: str
    name: str
    bank_id: str
    app_user_id: str
    habitica_user_id: str
    balance:int = 0
    account_type = "BankAccount"

@dataclass
class BankTransaction:
    id: str
    amount: float
    bank_id: str
    app_user_id: str 
    habitica_user_id: str
    bank_account_id: str
    description: str
    balance: float = 0.0
    src_completed: bool = False
    dst_completed: bool = False

    def dump(self):
        return asdict(self)
 
@dataclass
class Bank:
    id: str
    name: str
    owner: str
    funds: int = 0
    accounts: list[BankAccount] = field(default_factory=list[BankAccount])
    loan_accounts: list[BankLoanAccount] = field(default_factory=list[BankLoanAccount])

    def dump(self):
        return asdict(self)

    @staticmethod
    def load(model: dict):
        bank: Bank =  dacite.from_dict(Bank, model)
        return bank
