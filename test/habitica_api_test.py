import unittest
import habitica.habitica_api as api
import dotenv, os
from config import TEST_HABITICA_API_TOKEN, TEST_HABITICA_API_USER

class HabiticaAPITest(unittest.IsolatedAsyncioTestCase):
    async def test_get_user(self):
        user = await api.get_user(TEST_HABITICA_API_USER, TEST_HABITICA_API_TOKEN)
        self.assertIn('data',user)
        self.assertIn('id',user['data'])
    
    async def test_get_party(self):
        party = await api.get_party(TEST_HABITICA_API_USER, TEST_HABITICA_API_TOKEN)
        self.assertIn('data',party)
        self.assertIn('id',party['data'][0])

    async def test_get_tasks(self):
        tasks = await api.get_tasks(TEST_HABITICA_API_USER, TEST_HABITICA_API_TOKEN)
        self.assertIn('data',tasks)
    
    async def test_get_webhooks(self):
        webhooks = await api.get_webhooks(TEST_HABITICA_API_USER, TEST_HABITICA_API_TOKEN)
        self.assertIn('data',webhooks)
