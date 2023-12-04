import unittest
import habitica.habitica_api as api
import json
import habitica.model.user as User
import habitica.model.task as Task
from habitica.model import HabiticaParty, HabiticaTasks, HabiticaUser
from habitica.model import Webhook
import dotenv, os

dotenv.load_dotenv(".env")
HABITICA_API_USER = os.getenv("TEST_PROXY_HABITICA_USER_ID")
HABITICA_API_TOKEN = os.getenv("TEST_PROXY_HABITICA_API_TOKEN")

class HabiticaUserModelTest(unittest.IsolatedAsyncioTestCase):
    async def test_user_model(self):
        # user_dict = await api.get_user(HABITICA_API_USER, HABITICA_API_TOKEN)
        model_cases = []
        with open('test\\sample_data\\user_model_new_user.json','r') as fh:
            model_cases.append(json.load(fh))
        with open('test\\sample_data\\user_model.json','r') as fh:
            model_cases.append(json.load(fh))
        for user_dict in model_cases:
            
            # 'class' causes deserialization problems
            user_dict['data']['stats']['character_class'] = user_dict['data']['stats']['class']
            del user_dict['data']['stats']['class']

            user = HabiticaUser.load(user_dict)
            self.assertTrue(type(user.items) == User.Items)
            self.assertTrue(type(user.items.gear) == User.Gear)
            self.assertTrue(type(user.preferences.hair) == User.Hair)
            self.assertTrue(type(user.stats.character_class) == str)
            self.assertTrue(type(user.newMessages) == dict)
            
    async def test_party_model(self):
        with open('test\\sample_data\\party_model.json','r') as fh:
            party_json = json.load(fh)
            parties = HabiticaParty.load(party_json)
        self.assertTrue(type(parties[0].leader), str)

    async def test_task_model(self):
        with open('test\\sample_data\\tasks_model.json','r') as fh:
            task_json = json.load(fh)
            tasks = HabiticaTasks.load(task_json)
        self.assertTrue(type(tasks.daily[0]), Task.HabiticaDaily)
        self.assertTrue(type(tasks.habit[0]), Task.HabiticaHabit)
        self.assertTrue(type(tasks.todo[0]), Task.HabiticaTodo)
        self.assertTrue(type(tasks.reward[0]), Task.HabiticaReward)

    def test_webhook_model(self):
        expected = {
            'test\\sample_data\\taskActivity-daily.json': Task.HabiticaDaily,
            'test\\sample_data\\taskActivity-habit.json': Task.HabiticaHabit,
            'test\\sample_data\\taskActivity-reward.json': Task.HabiticaReward,
            'test\\sample_data\\taskActivity-todo.json': Task.HabiticaTodo,
        }
        for webhook_model, expected_class in expected.items():
            with open(webhook_model,'r') as fh:
                webhook_json = json.load(fh)
                webhook = Webhook.load(webhook_json)
            self.assertTrue(type(webhook.task), expected_class)
        