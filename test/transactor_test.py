from uuid import uuid4
import unittest

from attr import dataclass
import app.transaction_service as d
from loguru import logger
from app.app_user_service import AppUserService
from app.bank_service import BankAccount
from persistence.memory_driver_new import PersistenceMemoryDriver
import asyncio
class TransactorTest(unittest.IsolatedAsyncioTestCase):

    async def test_transaction(self):
        d.ledger = d.OperationLedger()
        bank_accounts = d.TransactableList()
        bank_account1 = BankAccount("id1","name1","bank1","app_user1","habitica_user1")
        bank_account2 = BankAccount("id2","name2","bank2","app_user2","habitica_user2")

        buttress = d.TransactableAttribute()


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

class TrasnsactableListTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        d.ledger = d.OperationLedger()
        self.bank_accounts = d.TransactableList()
        self.bank_account1 = BankAccount("id1","name1","bank1","app_user1","habitica_user1")
        self.bank_account2 = BankAccount("id2","name2","bank2","app_user2","habitica_user2")

    def test_transact_attribute(self):

        class Person:
            age = d.TransactableAttribute()
            def __init__(self, age) -> None:
                self.age = age

        person = Person(10)
        person.age = 22
        person.age += 10
        self.assertTrue(person.age, 32)
        operation = d.ledger.operations[-1]
        d.ledger.rollback(operation)
        self.assertTrue(person.age, 22)

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