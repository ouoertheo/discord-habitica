# Habitica Bank
from dataclasses import dataclass, asdict, field
import dacite

@dataclass
class BankLoanAccount:
    """
    Create a loan account.
    name: The name of the account
    app_user_id: the Habitica App User that owns the account
    """
    id: str
    name: str
    bank_user_id: str
    bank_id: str
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
    bank_user_id: str
    app_user_id: str
    balance:int = 0
    account_type = "BankAccount"

@dataclass
class BankUser:
    id: str
    app_user_id: str
    bank_id: str
    accounts: list[BankAccount] = field(default_factory=list)
    loan_accounts: list[BankLoanAccount] = field(default_factory=list)
 
@dataclass
class Bank:
    id: str
    name: str
    owner: str
    funds: int = 0
    users: list[BankUser] = field(default_factory=list)

    def dump(self):
        return asdict(self)

    @staticmethod
    def load(model: dict):
        bank: Bank =  dacite.from_dict(Bank, model)
        return bank