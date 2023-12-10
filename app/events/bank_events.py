from dataclasses import dataclass
#################
## Bank Events ##
#################

@dataclass
class CreateBank:
    bank_name: str
    habitica_api_user: str
    discord_channel_id: str
    type = "create_bank"


@dataclass
class DeleteBank:
    bank_id: str
    discord_channel: str
    type = "delete_bank"

@dataclass
class OpenAccount:
    account_name: str
    bank_id: str
    bank_user_id: str
    type = "open_account"

@dataclass
class OpenLoanAccount:
    account_name: str
    bank_id: str
    bank_user_id: str
    amount: float
    interest: float
    term: int
    type = "open_loan_account"

@dataclass
class CloseAccount:
    bank_user_id: str
    bank_id: str
    bank_account_name: str
    type = "close_account"

@dataclass
class DepositGold:
    amount: float
    bank_account_id: str
    bank_id: str
    bank_user_id: str
    type = "deposit_gold"

@dataclass
class RemoveGoldConfirmed:
    amount: float
    bank_account_id: str
    bank_id: str
    bank_user_id: str
    type = "deposit_gold_confirmed"

@dataclass
class WithdrawGold:
    amount: float
    bank_account_id: str
    bank_id: str
    app_user_id: str
    type = "withdraw_gold"

@dataclass
class WithdrawGoldConfirmed:
    amount: float
    bank_bank_account_id: str
    bank_id: str
    app_user_id: str
    type = "withdraw_gold_confirmed"

@dataclass
class ChargeBankPayment:
    amount: float
    bank_account_id: str
    bank_id: str
    app_user_id: str
    type = "charge_bank_payment"