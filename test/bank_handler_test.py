from typing import Any, Coroutine
import unittest
from app.handlers.bank_handlers import BankEventHandlers, AppUserService, BankService
from app.events import bank_events, event_service
from persistence.memory_driver_new import PersistenceMemoryDriver

class BankHandlerTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.driver = PersistenceMemoryDriver()
        self.bank_service = BankService(self.driver)
        self.app_user_service = AppUserService(self.driver)
        self.bank_event_handler = BankEventHandlers(self.bank_service, self.app_user_service)
        self.API_USER = "API_USER"
        self.API_TOKEN = "API_TOKEN"
        self.HABITICA_USER = "Knight1_Habitica"
        self.APP_USER_ID = "Knight1_DISCORD"
        self.DISCORD_CHANNEL_ID = "Forest"
        self.BANK_NAME = "Knights of Nih! Bank"

    async def test_handle_create_bank_event(self):
        app_user = self.app_user_service.create_app_user(self.APP_USER_ID)
        habitica_user_link = self.app_user_service.add_habitica_user_link(
            self.APP_USER_ID,
            self.API_USER,
            self.API_TOKEN,
            self.HABITICA_USER
            )
        await event_service.post_event(bank_events.CreateBank(
            self.BANK_NAME, 
            habitica_user_link.api_user
            ))
        bank = self.bank_service.get_bank(bank_name=self.BANK_NAME)
        self.assertEqual(bank.name, self.BANK_NAME)

