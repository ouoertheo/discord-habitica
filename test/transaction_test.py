from uuid import uuid4
import unittest
from dataclasses import dataclass, field
import app.transaction_service as d
from loguru import logger
from app.bank_service import BankAccount
class TransactionTest(unittest.IsolatedAsyncioTestCase):

    async def test_transaction(self):
        d.ledger = d.OperationLedger()
        bank_accounts = d.TransactableList()
        bank_account1 = BankAccount("id1","name1","bank1","app_user1","habitica_user1",0)
        bank_account2 = BankAccount("id2","name2","bank2","app_user2","habitica_user2",0)

        # Run operations within a transaction
        async with d.ledger as transaction:
            bank_accounts.append(bank_account1)
            bank_accounts.append(bank_account2)

        self.assertEqual(len(transaction.operations), 2) # Ensure both operations were recorded
        self.assertEqual(len(d.ledger.transactions), 1) # Ensure one transaction was recorded
        self.assertEqual(len(bank_accounts), 2) # Ensure only two bank accounts created
        self.assertIn(bank_account1, bank_accounts) # Double check bank account in list
        self.assertIn(bank_account2, bank_accounts) # Double check bank account in list

        with self.assertRaises(d.TransactionException):
            bank_accounts_2 = d.TransactableList()
            async with d.ledger as transaction:
                bank_accounts_2.append(bank_account1)
                bank_accounts_2.remove(bank_accounts_2)

        # Make sure bank_account1 was rolled back
        self.assertNotIn(bank_account1, bank_accounts_2)

class TransactableAttributeTest(unittest.TestCase):
    def test_transact_attribute(self):
        @dataclass
        class Person:
            age: d.TransactableAttribute = d.TransactableAttribute()

        person = Person(10)
        person.age = 22
        person.age += 10
        self.assertTrue(person.age, 32)
        operation = d.ledger.operations[-1]
        d.ledger.rollback(operation)
        self.assertTrue(person.age, 22)
class TrasnsactableListTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        d.ledger = d.OperationLedger()
        self.bank_accounts = d.TransactableList()
        self.bank_account1 = BankAccount("id1","name1","bank1","app_user1","habitica_user1",0)
        self.bank_account2 = BankAccount("id2","name2","bank2","app_user2","habitica_user2",0)

    def test_append_and_rollback(self):
        self.bank_accounts.append(self.bank_account1)
        self.bank_accounts.append(self.bank_account2)
        self.assertEqual(len(d.ledger.operations), 2)

        operation = d.ledger.get_operation(new_value=self.bank_account1)
        d.ledger.rollback(operation)

        self.assertNotIn(self.bank_account1, self.bank_accounts)
        self.assertEqual(len(self.bank_accounts), 1)

    def test_insert_and_rollback(self):
        self.bank_accounts.insert(0, self.bank_account1)
        self.assertEqual(self.bank_accounts[0], self.bank_account1)
        operation = d.ledger.operations[-1]
        
        d.ledger.rollback(operation)

        self.assertNotIn(self.bank_account1, self.bank_accounts)
        self.assertEqual(len(self.bank_accounts), 0)

    def test_delete_and_rollback(self):
        self.bank_accounts.append(self.bank_account2)
        self.bank_accounts.remove(self.bank_account2)
        operation = d.ledger.operations[-1]
        self.assertEqual(len(self.bank_accounts), 0)

        d.ledger.rollback(operation)
        self.assertEqual(len(self.bank_accounts), 1)
        self.assertIn(self.bank_account2, self.bank_accounts)

    def test_set_and_rollback(self):
        # Test set and rollback
        self.bank_accounts.append(self.bank_account2)
        self.bank_accounts[0] = self.bank_account1
        self.assertIn(self.bank_account1, self.bank_accounts)
        self.assertNotIn(self.bank_account2, self.bank_accounts)
        self.assertEqual(len(self.bank_accounts), 1)

        operation = d.ledger.operations[-1]
        d.ledger.rollback(operation)
        self.assertIn(self.bank_account2, self.bank_accounts)
        self.assertNotIn(self.bank_account1, self.bank_accounts)
        self.assertEqual(len(self.bank_accounts), 1)

import unittest

class TransactableDictTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        d.ledger = d.OperationLedger()
        self.bank_accounts = d.TransactableDict()
        self.bank_account1 = BankAccount("id1", "name1", "bank1", "app_user1", "habitica_user1", 0)
        self.bank_account2 = BankAccount("id2", "name2", "bank2", "app_user2", "habitica_user2", 0)

    def test_set_and_rollback(self):
        # Test set and rollback
        self.bank_accounts["account1"] = self.bank_account1
        self.bank_accounts["account2"] = self.bank_account2
        self.assertIn("account1", self.bank_accounts)
        self.assertIn("account2", self.bank_accounts)
        self.assertEqual(len(self.bank_accounts), 2)

        operation = d.ledger.operations[-1]
        d.ledger.rollback(operation)
        self.assertNotIn("account2", self.bank_accounts)
        self.assertEqual(len(self.bank_accounts), 1)

    def test_delete_and_rollback(self):
        self.bank_accounts["account2"] = self.bank_account2
        del self.bank_accounts["account2"]
        operation = d.ledger.operations[-1]
        self.assertEqual(len(self.bank_accounts), 0)

        d.ledger.rollback(operation)
        self.assertEqual(len(self.bank_accounts), 1)
        self.assertIn("account2", self.bank_accounts)

    def test_pop_and_rollback(self):
        self.bank_accounts["account1"] = self.bank_account1
        popped_account = self.bank_accounts.pop("account1")
        operation = d.ledger.operations[-1]
        self.assertEqual(popped_account, self.bank_account1)
        self.assertEqual(len(self.bank_accounts), 0)

        d.ledger.rollback(operation)
        self.assertEqual(len(self.bank_accounts), 1)
        self.assertIn("account1", self.bank_accounts)

    def test_update_and_rollback(self):
        self.bank_accounts["account1"] = self.bank_account1
        self.bank_accounts["account2"] = self.bank_account2

        # Test positional argument update
        updated_data = {"account1": BankAccount("id3", "name3", "bank3", "app_user3", "habitica_user3",0)}
        self.bank_accounts.update(updated_data)

        # Test keyword argument update
        self.bank_accounts.update(account2=BankAccount("id4", "name4", "bank4", "app_user4", "habitica_user4",0))

        operation = d.ledger.operations[-1]
        operation2 = d.ledger.operations[-2]

        self.assertEqual(self.bank_accounts["account1"].name, "name3")
        self.assertEqual(self.bank_accounts["account2"].name, "name4")

        d.ledger.rollback(operation)
        d.ledger.rollback(operation2)

        self.assertEqual(self.bank_accounts["account1"].name, "name1")
        self.assertEqual(self.bank_accounts["account2"].name, "name2")


if __name__ == '__main__':
    unittest.main()
