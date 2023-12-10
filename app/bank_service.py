from app.model.bank import Bank, BankLoanAccount, BankAccount
from persistence.driver_base_new import PersistenceDriverBase
from loguru import logger
from uuid import uuid4
from app.utils import match_all_in_list, ensure_one

class BankNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        logger.error(args[0])

class BankExistsException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        logger.error(args[0])

class BankUserExistsException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        logger.error(args[0])

class BankUserNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        logger.error(args[0])

class BankAccountExists(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        logger.error(args[0])

class BankAccountNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        logger.error(args[0])

class BankInsufficientFundsException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        logger.error(args[0])

class BankService:
    def __init__(self, persistence_driver: PersistenceDriverBase) -> None:
        self.driver = persistence_driver
        self.bank_store = self.driver.stores.BANK
        self.bank_user_store = self.driver.stores.BANK_USER
        self.bank_account_store = self.driver.stores.BANK_ACCOUNT
        self.banks: list[Bank] = []
        self.init_store()
    
    def init_store(self):
        banks_raw = self.driver.list(self.bank_store)
        for bank in banks_raw:
            self.banks.append(Bank.load(banks_raw[bank]))
        logger.info(f"Loaded {len(self.banks)} banks from store {self.bank_store}")

# TODO: Create separate stores for bank users, accounts, and banks. In order to do this, they won't be automatically
# imported via dacite and the object model relationships will need to be handled as special cases. This is acutally
# a pretty big refactor. Maybe that logic goes into the model code itself?

# TODO: On get calls, pull from persistence? This might affect how we change init, making the local banks more 
# of a cache. This could ensure that we are properly synced up with the persistence layer though. Is this necessary? 
# Also, I really feel like these should all be DB queries instead of querying memory. That's kinda a big thing for me though.

    ##################
    ## Manage Banks ##
    ##################

    def create_bank(self, bank_name, owner_id):
        """
        Create a new bank given the owner ID (typically a habitica api_user).

        Raises BankExistsException if bank name already exists.
        """
        if self.get_bank(bank_name=bank_name):
            raise BankExistsException(f"Bank with name {bank_name} already exists. Use a different name.")
        
        bank = Bank(str(uuid4()), bank_name, owner_id)
        self.banks.append(bank)

        self.driver.create(self.bank_store, bank.dump())
        logger.info(f"User {owner_id} created a new bank with name {bank_name}")
        return bank

    def delete_bank(self, bank_name):
        bank = self.get_bank(bank_name=bank_name)
        self.banks.remove(bank)

        self.driver.delete(self.bank_store, bank.id)
        logger.warning(f"Bank with {bank_name} deleted")

    def get_banks(self, bank_name="", bank_id="", bank_owner="") -> list[Bank]:
        """
        Get list of banks given criteria.
        If no creteria given or all criteria is Falsy, return all banks.
        Raises BankNotFoundException if no banks found.
        """
        banks = match_all_in_list(self.banks, id=bank_id, name=bank_name, owner=bank_owner)
        return banks

    @ensure_one
    def get_bank(self, bank_name="", bank_id="", bank_owner="") -> Bank:
        return self.get_banks(bank_name, bank_id, bank_owner)
    
    ###########################
    ## Manage Banks Accounts ##
    ###########################

    def open_account(self, account_name: str, bank_id: str, app_user_id:str, habitica_user_id: str):
        bank = self.get_bank(bank_id=bank_id)

        # Check if account is unique within the bank
        if self.get_account(bank_id=bank_id, habitica_user_id=habitica_user_id, bank_account_name=account_name):
            raise BankAccountExists(f"Bank account with name {account_name} already exists in bank {bank.name}")

        # Create the account and store it
        account = BankAccount(str(uuid4()), account_name, bank.id, app_user_id, habitica_user_id, 0)
        bank.accounts.append(account)
        
        self.driver.update(self.bank_store, bank.dump())
        logger.info(f"App user {habitica_user_id} opened account {account_name} in bank {bank_id}.")
        return account 
    
    def open_loan_account(self, account_name: str, bank_id, app_user_id: str, habitica_user_id:str, amount: float, interest: float, term: int):
        bank = self.get_bank(bank_id=bank_id)

        # Check if account is unique within the bank
        if self.get_account(bank_id=bank_id, habitica_user_id=habitica_user_id, bank_account_name=account_name):
            raise BankAccountExists(f"Bank account with name {account_name} already exists in bank.")
        
        # Create the account and store it
        account = BankLoanAccount(
            id=str(uuid4()),
            name=account_name,
            bank_id=bank.id, 
            habitica_user_id=habitica_user_id,
            app_user_id=app_user_id,
            amount=amount, 
            interest=interest, 
            term=term, 
            principal=amount
        )
        bank.loan_accounts.append(account)
        self.driver.update(self.bank_store, bank.dump())
        logger.info(f"Bank User {habitica_user_id} opened loan account {account_name} in bank {bank_id}.")
        return account

    def close_account(self, habitica_user_id, bank_id, bank_account_name):
        account = self.get_account(habitica_user_id=habitica_user_id, bank_id=bank_id, bank_account_name=bank_account_name)
        bank = self.get_bank(bank_id=bank_id)
        if account in bank.accounts:
            bank.accounts.remove(account)
        elif account in bank.loan_accounts:
            bank.loan_accounts.remove(account)

        self.driver.update(self.bank_store, self.get_bank(bank_id=bank_id).dump())
        logger.info(f"Bank User {habitica_user_id} closed account {bank_account_name} in bank {bank_id}")
    
    def get_accounts(self, bank_id="", app_user_id="", habitica_user_id="", bank_account_id="", bank_account_name="",account_type="") -> list[BankAccount | BankLoanAccount]:
        accounts = []
        banks = self.get_banks()
        # Get all accounts from all users
        for bank in banks:
            accounts += [account for account in bank.accounts]
            accounts += [account for account in bank.loan_accounts]
        
        # Filter accounts by conditions.
        accounts = match_all_in_list(accounts, 
                                          bank_id=bank_id,
                                          app_user_id=app_user_id,
                                          habitica_user_id=habitica_user_id, 
                                          id=bank_account_id,
                                          name=bank_account_name,
                                          account_type=account_type
                                          )
        return accounts
    
    @ensure_one
    def get_account(self, bank_id="", app_user_id="", habitica_user_id="", bank_account_id="", bank_account_name="",account_type="") -> BankAccount | BankLoanAccount | None:
        return self.get_accounts(bank_id, app_user_id, habitica_user_id, bank_account_id, bank_account_name,account_type)
    
    ##############################
    ## Manage Bank Transactions ##
    ##############################

    def deposit(self, amount, bank_account_id, habitica_user_id, bank_id):
        "Deposit money. Returns the new balance"
        account = self.get_account(bank_id=bank_id, habitica_user_id=habitica_user_id, bank_account_id=bank_account_id, account_type="BankAccount")
        account.balance += amount
        
        self.driver.update(self.bank_store, self.get_bank(bank_id=bank_id).dump())
        logger.info(f"Habitica User {habitica_user_id} deposited {amount} GP into {account.name} in bank {bank_id}")
        return account.balance
    
    def withdraw(self, amount, bank_account_id, habitica_user_id, bank_id):
        "Withdraw money. Returns the new balance"
        account = self.get_account(bank_id=bank_id, habitica_user_id=habitica_user_id, bank_account_id=bank_account_id, account_type="BankAccount")

        if account.balance - amount < 0:
            raise BankInsufficientFundsException(f"Account {account.name} has insufficient funds to withdraw {amount}. Current balance is {account.balance}")
        account.balance -= amount

        self.driver.update(self.bank_store, self.get_bank(bank_id=bank_id).dump())
        logger.info(f"Habitica User {habitica_user_id} withdrew {amount} GP from {account.name} in bank {bank_id}")
        return account.balance
    
    def calculate_payment(self, bank_account_id, habitica_user_id, bank_id):
        account = self.get_account(bank_id=bank_id, habitica_user_id=habitica_user_id, bank_account_id=bank_account_id, account_type="BankLoanAccount")
        interest = (account.principal - account.balance) * account.interest
        payment = (account.principal / account.term) + interest
        return payment