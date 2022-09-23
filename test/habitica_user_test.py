import unittest
from habitica.habitica_user import HabiticaUser, api, WebHook
from config import DRIVER
import dotenv, os

dotenv.load_dotenv(".env")
HABITICA_API_USER = os.getenv("TEST_PROXY_HABITICA_USER_ID")
HABITICA_API_TOKEN = os.getenv("TEST_PROXY_HABITICA_API_TOKEN")

class HabiticaUserTest(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_user_details(self):
        user = HabiticaUser(HABITICA_API_USER, HABITICA_API_TOKEN)
        await user.fetch_user_details()
        self.assertTrue(user.user_name)
        self.assertTrue(user.user_id)
    
    async def test_fetch_webhooks(self):
        user = HabiticaUser(HABITICA_API_USER, HABITICA_API_TOKEN)
        webhook = WebHook(WebHook.TASK, "test_user_id")
        test_webhook = await api.create_webhook(HABITICA_API_USER, HABITICA_API_TOKEN, webhook.payload)
        await user.fetch_webhooks()
        await api.delete_webhook(HABITICA_API_USER, HABITICA_API_TOKEN, test_webhook['data']['id'])
        user_webhook = [wh.id for wh in user.webhooks if wh.id == test_webhook['data']['id']]
        self.assertIn(test_webhook['data']['id'], user_webhook)

    async def test_dump():
        user = HabiticaUser(HABITICA_API_USER, HABITICA_API_TOKEN)

        


