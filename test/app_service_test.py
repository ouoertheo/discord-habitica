import unittest
from app.app_service import AppService
from app.app_user_service import HabiticaUserLinkExists
from app.app_user_service import AppUserService
from app.bank_service import BankService
from habitica.habitica_service import HabiticaService
from app.events import event_service, app_events
import habitica_api_mock as mock_api
from persistence.memory_driver_new import PersistenceMemoryDriver

class DiscordHabiticaTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
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
        self.HABITICA_API_USER = "api_user"
        self.HABITICA_API_TOKEN = "api_token"
        self.APP_USER_ID = "discord_user"
        self.DISCORD_CHANNEL = "discord_channel"

    async def test_handler_register_habitica_account(self):
        app = self.app
        event = app_events.RegisterHabiticaAccount(self.APP_USER_ID, self.DISCORD_CHANNEL, self.HABITICA_API_USER, self.HABITICA_API_TOKEN)
        await app.register_habitica_account(event)
        habitica_user = app.app_user_service.get_app_user(app_user_id=self.APP_USER_ID)
        self.assertEqual(habitica_user.id, self.APP_USER_ID)
        self.assertEqual(app.app_user_service.get_habitica_user_link(app_user_id=self.APP_USER_ID).app_user_id,self.APP_USER_ID)

        # Should raise Habitica Account Exists 
        with self.assertRaises(HabiticaUserLinkExists):
            await app.register_habitica_account(app_events.RegisterHabiticaAccount(self.APP_USER_ID, self.DISCORD_CHANNEL, self.HABITICA_API_USER, self.HABITICA_API_TOKEN))
    



