import unittest
from app.model.bank import Bank, BankAccount
import app.bank_service as bank_service
from persistence.driver_base_new import PersistenceDriverBase
from persistence.memory_driver_new import PersistenceMemoryDriver

class BankServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = PersistenceMemoryDriver()
        self.bank_service = bank_service.BankService(self.driver)
        self.bank = self.bank_service.create_bank("Bank of Shrubberies","Knights")
    
    def duplicate_service(self):
        # Verify persistence creating a new bank service with copy and testing user is in there.
        duplicate_bank_service = bank_service.BankService(PersistenceMemoryDriver())
        duplicate_bank_service.driver.store_cache = self.bank_service.driver.store_cache
        duplicate_bank_service.init_store()
        return duplicate_bank_service
    
    def test_create_bank(self):
        bank = self.bank_service.create_bank("Bank of Nih!","Knights")
        self.assertEqual(bank.name, "Bank of Nih!")

        # Test persistence
        bank_service2 = self.duplicate_service()
        self.assertEqual(bank_service2.get_bank(bank_id=bank.id).name, "Bank of Nih!")

    
    def test_delete_bank(self):
        bank = self.bank_service.create_bank("Bank of Nih!","Knights")
        self.assertEqual(bank.name, "Bank of Nih!")
        self.bank_service.delete_bank(bank.name)
        self.assertNotIn(bank, self.bank_service.get_banks(bank_id=bank.id))

        # Test persistence
        bank_service2 = self.duplicate_service()
        self.assertNotIn(bank, bank_service2.get_banks(bank_id=bank.id))
    
    def test_get_banks(self):
        bank_id = self.bank_service.create_bank("Bank of Nih!","Knights").id
        self.bank_service.create_bank("Bank of Spam","Vikings")
        self.bank_service.create_bank("Bank of Spam and Bacon","Vikings")

        # Test getting multiple by owner
        self.assertEqual(len(self.bank_service.get_banks(bank_owner="Vikings")), 2)

        # Test getting by id
        self.assertEqual(self.bank_service.get_banks(bank_id=bank_id)[0].id, bank_id)

        # Test getting by name
        self.assertEqual(self.bank_service.get_banks(bank_name="Bank of Spam")[0].name, "Bank of Spam")

        # Test multiple criteria
        self.assertEqual(self.bank_service.get_banks(bank_id=bank_id, bank_owner="Knights")[0].id, bank_id)
    

    def test_open_and_get_account(self):
        user1 = "user1"
        account = self.bank_service.open_account("Nih! Checking", self.bank.id, user1, user1)
        
        accounts = self.bank_service.get_accounts(habitica_user_id=user1)
        self.assertIn(account, accounts)
        
        accounts = self.bank_service.get_accounts(app_user_id=user1)
        self.assertIn(account, accounts)

        accounts = self.bank_service.get_accounts(bank_id=self.bank.id)
        self.assertIn(account, accounts)

        accounts = self.bank_service.get_accounts(bank_account_id=account.id)
        self.assertIn(account, accounts)

        accounts = self.bank_service.get_accounts(bank_account_name=account.name)
        self.assertIn(account, accounts)

        accounts = self.bank_service.get_accounts(account_type="BankAccount")
        self.assertIn(account, accounts)
        
        accounts = self.bank_service.get_accounts()
        self.assertIn(account, accounts)
        
        # Test persistence
        bank_service2 = self.duplicate_service()
        accounts = bank_service2.get_accounts()
        self.assertIn(account, accounts)


    def test_open_loan_account(self):
        user1 = "user1"
        account = self.bank_service.open_loan_account("Nih! Loan", self.bank.id, user1, user1, 1000.0, 0.03, 50)
        accounts = self.bank_service.get_accounts(habitica_user_id=user1, account_type="BankLoanAccount")
        self.assertIn(account, accounts)
        
        # Test persistence
        bank_service2 = self.duplicate_service()
        accounts = bank_service2.get_accounts(habitica_user_id=user1, account_type="BankLoanAccount")
        self.assertIn(account, accounts)

    def test_close_account(self):
        app_user_id = "user1"
        habitica_user_id = "user1"
        account_name = "test_account"
        loan_account_name = "test_loan_account"

        account = self.bank_service.open_account(account_name, self.bank.id, app_user_id, habitica_user_id)
        loan_account = self.bank_service.open_loan_account(loan_account_name,self.bank.id, app_user_id, habitica_user_id, 1000.0, 0.03, 50)

        self.assertIn(account, self.bank.accounts)
        self.assertIn(loan_account, self.bank.loan_accounts)

        self.bank_service.close_account(app_user_id, self.bank.id, account_name)
        self.bank_service.close_account(app_user_id, self.bank.id, loan_account_name)

        self.assertNotIn(account, self.bank.accounts)
        self.assertNotIn(loan_account, self.bank.loan_accounts)

        # Test persistence
        bank_service2 = self.duplicate_service()
        account = bank_service2.get_account(bank_account_name=account_name)
        loan_account = bank_service2.get_account(bank_account_name=loan_account_name)

        self.assertNotIn(account, self.bank.accounts)
        self.assertNotIn(loan_account, self.bank.loan_accounts)
    
    def test_deposit(self):
        app_user_id = "user1"
        habitica_user_id = "user1"
        account_name = "test_account"

        account = self.bank_service.open_account(account_name, self.bank.id, app_user_id, habitica_user_id)
        self.bank_service.deposit(100, account.id, self.bank.id)
        self.assertEqual(account.balance, 100)
        
        # Test persistence
        bank_service2 = self.duplicate_service()
        account = bank_service2.get_account(bank_account_name=account_name, bank_id=self.bank.id, habitica_user_id=app_user_id)
        self.assertEqual(account.balance, 100)

    def test_withdraw(self):
        app_user_id = "Knight1"
        habitica_user_id = "Knight1"
        account_name = "test_account"
        
        account = self.bank_service.open_account(account_name, self.bank.id, app_user_id, habitica_user_id)
        self.bank_service.deposit(100, account.id, self.bank.id)
        self.assertEqual(account.balance, 100)

        self.bank_service.withdraw(50, account.id, self.bank.id)
        self.assertEqual(account.balance, 50)
        
        # Test persistence
        bank_service2 = self.duplicate_service()
        account = bank_service2.get_account(bank_account_name=account_name, bank_id=self.bank.id, habitica_user_id=app_user_id)
        self.assertEqual(account.balance, 50)

    def test_calculate_payment(self):
        app_user_id = "Knight1"
        habitica_user_id = "Knight1"
        account = self.bank_service.open_loan_account("Nih! Loan", self.bank.id, app_user_id, habitica_user_id, 1000.0, 0.03, 50)
        self.assertTrue(self.bank_service.calculate_payment(account.id, self.bank.id), 50)

    def test_load_and_dump(self):
        app_user_id = "Knight1"
        habitica_user_id = "Knight1"
        account_name = "test_account"
        account = self.bank_service.open_account(account_name, self.bank.id, app_user_id, habitica_user_id)

        model = self.bank.dump()

        loaded_bank:Bank = Bank.load(model)
        loaded_bank.name = "Loaded Bank"
        self.bank_service.banks.append(loaded_bank)
        self.assertIn(loaded_bank.owner, self.bank.owner)
        
        loaded_account = self.bank_service.get_accounts(bank_id=loaded_bank.id,habitica_user_id=app_user_id)[0]
        self.assertEqual(loaded_account.name, account_name)
