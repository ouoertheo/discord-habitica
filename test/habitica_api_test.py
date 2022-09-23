import unittest
import habitica.habitica_api as api
import dotenv, os
from habitica.habitica_webhook import WebHook

dotenv.load_dotenv(".env")
HABITICA_API_USER = os.getenv("TEST_PROXY_HABITICA_USER_ID")
HABITICA_API_TOKEN = os.getenv("TEST_PROXY_HABITICA_API_TOKEN")

class HabiticaAPITest(unittest.IsolatedAsyncioTestCase):
    async def test_get_user(self):
        user = await api.get_user(HABITICA_API_USER, HABITICA_API_TOKEN)
        self.assertIn('data',user)
        self.assertIn('id',user['data'])
    
    async def test_get_party(self):
        party = await api.get_party(HABITICA_API_USER, HABITICA_API_TOKEN)
        self.assertIn('data',party)
        self.assertIn('id',party['data'])
    
    async def test_get_webhooks(self):
        webhooks = await api.get_webhooks(HABITICA_API_USER, HABITICA_API_TOKEN)
        self.assertIn('data',webhooks)

    async def test_webhooks(self):
        task_webhook = WebHook(WebHook.TASK, "test_user_id")
        webhook = await api.create_webhook(HABITICA_API_USER, HABITICA_API_TOKEN, task_webhook.payload)
        self.assertEqual(webhook['data']['type'], WebHook.TASK)
        self.assertEquals(webhook['data']['options'], task_webhook.TASK_OPTIONS)
        webhook_id = webhook['data']['id']
        await api.delete_webhook(HABITICA_API_USER, HABITICA_API_TOKEN,webhook_id)
        webhooks = await api.get_webhooks(HABITICA_API_USER, HABITICA_API_TOKEN)
        webhook = [wh for wh in webhooks['data'] if wh['id'] == webhook_id]
        self.assertFalse(webhook)
        