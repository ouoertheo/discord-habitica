import unittest
from habitica.habitica_group import HabiticaGroup
import dotenv, os

dotenv.load_dotenv(".env")
HABITICA_API_USER = os.getenv("TEST_PROXY_HABITICA_USER_ID")
HABITICA_API_TOKEN = os.getenv("TEST_PROXY_HABITICA_API_TOKEN")

class HabiticaGroupTest(unittest.IsolatedAsyncioTestCase):
    async def test_set_integration_user_id(self):
        group = HabiticaGroup("test_id","test_channel")
        user = await group.register_user(HABITICA_API_USER, HABITICA_API_TOKEN)
        await group.set_integration_user_id(user.user_id)
        integration_user = group.integration_user
        self.assertEqual(integration_user.webhooks)
