import unittest
from habitica.habitica_user import HabiticaUser, api, WebHook
from config import DRIVER
import dotenv, os
from persistence.file_driver import PersistenceFileDriver

dotenv.load_dotenv(".env")
HABITICA_API_USER = os.getenv("TEST_PROXY_HABITICA_USER_ID")
HABITICA_API_TOKEN = os.getenv("TEST_PROXY_HABITICA_API_TOKEN")

TEST_STORE = "test_store"
TEST_IMPLEMENTATION = PersistenceFileDriver 

class HabiticaUserTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.fd = TEST_IMPLEMENTATION("test_store")
        for store in self.fd.file_stores.values():
            os.remove(store)
        self.fd.verify_files()

    async def test_fetch_user_details(self):
        user = HabiticaUser(HABITICA_API_USER, HABITICA_API_TOKEN, "discord_user_id")
        await user.fetch_user_details()
        self.assertTrue(user.user_name)
        self.assertTrue(user.user_id)
    
    async def test_fetch_webhooks(self):
        user = HabiticaUser(HABITICA_API_USER, HABITICA_API_TOKEN, "discord_user_id")
        webhook = WebHook(WebHook.TASK, "test_user_id")
        test_webhook = await api.create_webhook(HABITICA_API_USER, HABITICA_API_TOKEN, webhook.payload)
        await user.fetch_webhooks()
        await api.delete_webhook(HABITICA_API_USER, HABITICA_API_TOKEN, test_webhook['data']['id'])
        user_webhook = [wh.id for wh in user.webhooks if wh.id == test_webhook['data']['id']]
        self.assertIn(test_webhook['data']['id'], user_webhook)

    async def test_dump(self):
        expected_user = HabiticaUser(HABITICA_API_USER, HABITICA_API_TOKEN, "discord_user_id")
        expected_user.driver = self.fd
        await expected_user.dump()
        returned_user = self.fd.get_user(expected_user.api_user)
        self.assertEqual(expected_user.api_user, returned_user['api_user'])