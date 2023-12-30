import unittest
from app.model.app_user import AppUser
from app.app_service import AppService
from app.app_user_service import HabiticaUserLinkExists
from app.app_user_service import AppUserService
from app.bank_service import BankService
from habitica.habitica_service import HabiticaService
import test.habitica_api_mock as mock_api
from persistence.memory_driver_new import PersistenceMemoryDriver
import config

class DiscordHabiticaTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.driver = PersistenceMemoryDriver()
        self.app_user_service = AppUserService(self.driver)
        self.bank_service = BankService(self.driver)
        self.habitica_service = HabiticaService(mock_api)
        self.app = AppService(
            mock_api, 
            PersistenceMemoryDriver(), 
            self.app_user_service, 
            self.bank_service,
            self.habitica_service
            )
        self.HABITICA_API_USER = config.TEST_HABITICA_API_USER
        self.HABITICA_API_TOKEN = config.TEST_HABITICA_API_USER
        self.APP_USER_ID = "discord_user_id"
        self.APP_USER_NAME = "discord_user_name"
        self.DISCORD_CHANNEL = "discord_channel"

    async def test_handler_register_habitica_account(self):
        app = self.app
        await app.register_habitica_account(self.APP_USER_ID, self.APP_USER_NAME, self.DISCORD_CHANNEL, self.HABITICA_API_USER, self.HABITICA_API_TOKEN)
        habitica_user = app.app_user_service.get_app_user(app_user_id=self.APP_USER_ID)
        self.assertEqual(habitica_user.id, self.APP_USER_ID)
        self.assertEqual(app.app_user_service.get_habitica_user_link(app_user_id=self.APP_USER_ID).app_user_id,self.APP_USER_ID)

        # Should raise Habitica Account Exists 
        with self.assertRaises(HabiticaUserLinkExists):
            await app.register_habitica_account(self.APP_USER_ID, self.APP_USER_NAME, self.DISCORD_CHANNEL, self.HABITICA_API_USER, self.HABITICA_API_TOKEN)
    
    async def test_get_status_message(self):
        bank_account_name = "My Bank Account"
        app_user = self.app_user_service.create_app_user(self.APP_USER_ID, self.APP_USER_NAME)
        habitica_user = self.app_user_service.add_habitica_user_link(app_user.id, self.HABITICA_API_USER,\
                                                                     self.HABITICA_API_TOKEN, "habitica_user")
        bank = self.bank_service.create_bank("Bank","owner")
        self.bank_service.open_account(bank_account_name,bank.id,self.APP_USER_ID,habitica_user.api_user)
        message = await self.app.get_status_message(app_user.id)

        # Assert some specific details are in message
        self.assertIn(bank_account_name, message)
        self.assertIn("warrior", message)


