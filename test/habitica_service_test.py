import unittest
from habitica.habitica_service import HabiticaService
import config as cfg
cfg.DRIVER.base_dir = "test_store"


class TestHabiticaService(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.service = HabiticaService()
    
    async def test_register_user(self):
        user = await self.service.register_user("api_user","api_token","discord_user_id","discrod_channel_id")

    async def test_register_group(self):
        pass

    def test_load_users(self):
        service = HabiticaService()
        pass
    
    def test_sync_webhook(self):
        pass

    

    
        
