import unittest
from habitica.habitica_service import HabiticaService, InsufficientGoldException
import app.events.event_service as event_service
import app.events.habitica_events as habitica_events
import os, dotenv
import config
API_USER = config.TEST_HABITICA_API_USER
API_TOKEN = config.TEST_HABITICA_API_TOKEN

class HabiticaServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.habitica_service = HabiticaService()
    
    @unittest.skip('Caused 504')
    async def test_create_and_delete_all_webhooks(self):
        hs = HabiticaService()
        evt = habitica_events.CreateAllWebhookSubscription(API_USER, API_TOKEN)
        await event_service.post_event(evt)
        
        user = await hs.get_user(API_USER, API_TOKEN)
        webhooks = [w['type'] for w in user.webhooks if 'Discord Habitica' in w['label']]
        self.assertIn('groupChatReceived', webhooks)
        self.assertIn('questActivity', webhooks)
        self.assertIn('userActivity', webhooks)
        self.assertIn('taskActivity', webhooks)

        evt = habitica_events.DeleteAllWebhookSubscription(API_USER, API_TOKEN)
        await event_service.post_event(evt)

        user = await hs.get_user(API_USER, API_TOKEN)
        webhooks = [w['type'] for w in user.webhooks if 'Discord Habitica' in w['label']]
        self.assertEqual(len(webhooks), 0)

    async def test_get_user(self):
        user = await self.habitica_service.get_user(API_USER, API_TOKEN)
        self.assertEqual(user.id, API_USER)
    
    async def test_add_user_gold(self):
        user = await self.habitica_service.get_user(API_USER, API_TOKEN)
        
        starting_gold = user.stats.gp
        amount = 20

        # Send event to add gold
        await self.habitica_service.add_user_gold(API_USER, API_TOKEN, amount)
        user = await self.habitica_service.get_user(API_USER, API_TOKEN)
        self.assertEqual(starting_gold + amount, user.stats.gp)

        # Send event to remove gold 
        await self.habitica_service.add_user_gold(API_USER, API_TOKEN, -amount)
        user = await self.habitica_service.get_user(API_USER, API_TOKEN)
        self.assertEqual(starting_gold, user.stats.gp)

        # Make sure InsufficientGoldException is raised
        with self.assertRaises(InsufficientGoldException):
            await self.habitica_service.add_user_gold(API_USER, API_TOKEN, -2000000)



        