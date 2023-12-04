import unittest
import habitica.habitica_api as api
import dotenv, os

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
        self.assertIn('id',party['data'][0])

    async def test_get_tasks(self):
        tasks = await api.get_tasks(HABITICA_API_USER, HABITICA_API_TOKEN)
        self.assertIn('data',tasks)
    
    async def test_get_webhooks(self):
        webhooks = await api.get_webhooks(HABITICA_API_USER, HABITICA_API_TOKEN)
        self.assertIn('data',webhooks)
