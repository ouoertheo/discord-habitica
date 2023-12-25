# Habitica Bank
from dataclasses import dataclass, asdict, field
from datetime import date
import dacite
from dacite import Config
from app.transaction_service import TransactableAttribute
@dataclass
class BankLoanAccount:
    """
    A loan account.

    `name`: The name of the account
    `bank_id`: id of the owning bank
    `app_user_id`: the Habitica App User that owns the account
    `habitica_user_id`: id of the habitica user
    `principal`: the current amount of the loan used to calculate interest
    `dpr`: the monthly percentage rate used to calculate interest
    `term`: the duration of the loan
    `balance`: the current balance of the loan account able to be used
    """
    id: str
    name: str
    bank_id: str
    app_user_id: str
    habitica_user_id: str
    principal: float
    mpr: float
    term_days: int
    balance: TransactableAttribute = TransactableAttribute()
    opened_date: date = None
    account_type = "BankLoanAccount"

@dataclass
class BankAccount:
    id: str
    name: str
    bank_id: str
    app_user_id: str
    habitica_user_id: str
    balance: TransactableAttribute = TransactableAttribute()
    account_type = "BankAccount"

 
@dataclass
class Bank:
    id: str
    name: str
    owner: str
    funds: int = 0
    loan_apr: float = 0.03
    accounts: list[BankAccount] = field(default_factory=list[BankAccount])
    loan_accounts: list[BankLoanAccount] = field(default_factory=list[BankLoanAccount])

    def dump(self):
        return asdict(self)

    @staticmethod
    def load(model: dict):
        
        def transform_balance(value):
            return TransactableAttribute(value)
        
        config = Config(type_hooks={TransactableAttribute: transform_balance})
        bank: Bank =  dacite.from_dict(Bank, model, config=config)
        return bank
