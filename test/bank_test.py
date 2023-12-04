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
    
    def test_create_and_get_user(self):
        user1 = self.bank_service.create_user(self.bank.id, "Knight1")
        user2 = self.bank_service.create_user(self.bank.id, "Knight2")

        # Test Raises error
        with self.assertRaises(bank_service.BankUserExistsException):
            self.bank_service.create_user(self.bank.id, user1.app_user_id)

        # Test getting user by app_user_id
        return_user = self.bank_service.get_users(app_user_id=user1.app_user_id)[0]
        self.assertEqual(return_user.app_user_id, user1.app_user_id)

        # Test getting ser by bank_user_id
        return_user = self.bank_service.get_users(bank_user_id=user1.id)[0]
        self.assertEqual(return_user.id, user1.id)

        # Test getting all users from bank
        self.assertIn(user1, self.bank_service.get_users(bank_ids=[self.bank.id]))
        self.assertIn(user2, self.bank_service.get_users(bank_ids=[self.bank.id]))

        # Test persistence
        bank_service2 = self.duplicate_service()
        self.assertIn(user1, bank_service2.get_users(bank_ids=[self.bank.id]))
        self.assertIn(user2, bank_service2.get_users(bank_ids=[self.bank.id]))

    def test_delete_bank_user(self):
        user1 = self.bank_service.create_user(self.bank.id, "Knight1")
        self.assertIn(user1, self.bank_service.get_users(bank_ids=[self.bank.id]))

        bank_service2 = self.duplicate_service()
        self.assertIn(user1, bank_service2.get_users(bank_ids=[self.bank.id]))

        # Testing user is not there
        self.bank_service.delete_user(self.bank.id, user1.app_user_id)
        self.assertNotIn(user1, self.bank_service.get_users(bank_ids=[self.bank.id]))
        
        # Test persistence
        bank_service2 = self.duplicate_service()
        self.assertNotIn(user1, bank_service2.get_users(bank_ids=[self.bank.id]))

    def test_open_and_get_account(self):
        user1 = self.bank_service.create_user(self.bank.id, "Knight1")
        account = self.bank_service.open_account("Nih! Checking",self.bank.id,user1.id)
        accounts = self.bank_service.get_accounts(bank_user_id=user1.id)
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
        user1 = self.bank_service.create_user(self.bank.id, "Knight1")
        account = self.bank_service.open_loan_account("Nih! Loan", self.bank.id, user1.id, 1000.0, 0.03, 50)
        accounts = self.bank_service.get_accounts(bank_user_id=user1.id, account_type="BankLoanAccount")
        self.assertIn(account, accounts)
        
        # Test persistence
        bank_service2 = self.duplicate_service()
        accounts = bank_service2.get_accounts(bank_user_id=user1.id, account_type="BankLoanAccount")
        self.assertIn(account, accounts)

    def test_close_account(self):
        app_user_id = "user1"
        account_name = "test_account"
        loan_account_name = "test_loan_account"
        user = self.bank_service.create_user(self.bank.id, app_user_id)
        account = self.bank_service.open_account(account_name, self.bank.id, user.id)
        loan_account = self.bank_service.open_loan_account(loan_account_name,self.bank.id, user.id, 1000.0, 0.03, 50)

        self.assertIn(account, user.accounts)
        self.assertIn(loan_account, user.loan_accounts)

        self.bank_service.close_account(user.id, self.bank.id, account_name)
        self.bank_service.close_account(user.id, self.bank.id, loan_account_name)

        self.assertNotIn(account, user.accounts)
        self.assertNotIn(loan_account, user.loan_accounts)

        # Test persistence
        bank_service2 = self.duplicate_service()
        account = bank_service2.get_account(bank_account_name=account_name)
        loan_account = bank_service2.get_account(bank_account_name=loan_account_name)

        self.assertNotIn(account, user.accounts)
        self.assertNotIn(loan_account, user.loan_accounts)
    
    def test_deposit(self):
        app_user_id = "user1"
        account_name = "test_account"
        user = self.bank_service.create_user(self.bank.id, app_user_id)
        account = self.bank_service.open_account(account_name, self.bank.id, user.id)
        self.bank_service.deposit(100, account.id, user.id, self.bank.id)
        self.assertEqual(account.balance, 100)
        
        # Test persistence
        bank_service2 = self.duplicate_service()
        account = bank_service2.get_account(bank_account_name=account_name, bank_id=self.bank.id, bank_user_id=user.id)
        self.assertEqual(account.balance, 100)

    def test_withdraw(self):
        app_user_id = "user1"
        account_name = "test_account"
        user = self.bank_service.create_user(self.bank.id, app_user_id)
        account = self.bank_service.open_account(account_name, self.bank.id, user.id)
        self.bank_service.deposit(100, account.id, user.id, self.bank.id)
        self.assertEqual(account.balance, 100)

        self.bank_service.withdraw(50, account.id, user.id, self.bank.id)
        self.assertEqual(account.balance, 50)
        
        # Test persistence
        bank_service2 = self.duplicate_service()
        account = bank_service2.get_account(bank_account_name=account_name, bank_id=self.bank.id, bank_user_id=user.id)
        self.assertEqual(account.balance, 50)

    def test_calculate_payment(self):
        user1 = self.bank_service.create_user(self.bank.id, "Knight1")
        account = self.bank_service.open_loan_account("Nih! Loan", self.bank.id, user1.id, 1000.0, 0.03, 50)
        self.assertTrue(self.bank_service.calculate_payment(account.id,user1.id, self.bank.id), 50)

    def test_load_and_dump(self):
        app_user_id = "user1"
        account_name = "test_account"
        user = self.bank_service.create_user(self.bank.id, app_user_id)
        account = self.bank_service.open_account(account_name, self.bank.id, user.id)

        model = self.bank.dump()
        self.assertIn(account.name, [account_name['name'] for account_name in model["users"][0]["accounts"]])

        loaded_bank:Bank = Bank.load(model)
        loaded_bank.name = "Loaded Bank"
        self.bank_service.banks.append(loaded_bank)
        self.assertIn(loaded_bank.owner, self.bank.owner)
        loaded_user = self.bank_service.get_users(bank_user_id=user.id, bank_ids=[loaded_bank.id])[0]
        loaded_account = self.bank_service.get_accounts(bank_id=loaded_bank.id,bank_user_id=loaded_user.id)[0]
        self.assertEqual(loaded_user.id, user.id)
        self.assertEqual(loaded_account.name, account_name)


