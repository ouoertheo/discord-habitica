from persistence.file_driver import PersistenceFileDriver 
from habitica.habitica_webhook import WebHook
import unittest
import os
import json

TEST_STORE = "test_store"
TEST_IMPLEMENTATION = PersistenceFileDriver
class FileDriverTest(unittest.TestCase):

    def setUp(self) -> None:
        fd = TEST_IMPLEMENTATION("test_store")
        for store in fd.file_stores.values():
            os.remove(store)
        fd.verify_files()

    def test_verify_files(self):
        fd = TEST_IMPLEMENTATION("test_store")
        fd.verify_files()
        for store in fd.file_stores:
            self.assertTrue(os.path.exists(fd.file_stores[store]))

    def test_create_user(self):
        fd = TEST_IMPLEMENTATION("test_store")
        fd.create_user("test_id","test_name","test_api_user","test_api_token","test_group_id")
        with open(fd.file_stores["user"], 'r') as user_store:
            users = json.load(user_store)
        user = users["test_id"]
        self.assertEquals(user["id"], "test_id")

    def test_get_user_by_id(self):
        fd = TEST_IMPLEMENTATION("test_store")
        fd.create_user("test_id","test_name","test_api_user","test_api_token","test_group_id")
        user = fd.get_user_by_id("test_id")
        self.assertEquals(user["id"], "test_id")
    
    def test_get_user_by_api(self):
        fd = TEST_IMPLEMENTATION("test_store")
        fd.create_user("test_id","test_name","test_api_user","test_api_token","test_group_id")
        user = fd.get_user_by_api("test_api_user")
        self.assertEquals(user["id"], "test_id")
    
    def test_get_user_by_name(self):
        fd = TEST_IMPLEMENTATION("test_store")
        fd.create_user("test_id","test_name","test_api_user","test_api_token","test_group_id")
        user = fd.get_user_by_name("test_name")
        self.assertEquals(user["id"], "test_id")
    
    def test_update_user_group(self):
        fd = TEST_IMPLEMENTATION("test_store")
        fd.create_user("test_id","test_name","test_api_user","test_api_token","test_group_id")
        user = fd.get_user_by_name("test_name")
        user = fd.update_user_group(user["id"],"new_test_group_id")
        self.assertEquals(user["group_id"], "new_test_group_id")

    def test_create_integration_user(self):
        fd = TEST_IMPLEMENTATION("test_store")
        fd.create_integration_user("test_api_user","test_api_token","test_group_id")
        with open(fd.file_stores["integration_user"], 'r') as store:
            integration_users = json.load(store)
        integration_user = integration_users["test_api_user"]
        self.assertEquals(integration_user["api_user"], "test_api_user")

    def test_get_integration_user_by_id(self):
        fd = TEST_IMPLEMENTATION("test_store")
        fd.create_integration_user("test_api_user","test_api_token","test_group_id")
        integration_user = fd.get_integration_user("test_api_user")
        self.assertEquals(integration_user["api_user"], "test_api_user")
    
    def test_update_integration_user_group(self):
        fd = TEST_IMPLEMENTATION("test_store")
        fd.create_integration_user("test_api_user","test_api_token","test_group_id")
        integration_user = fd.get_integration_user("test_api_user")
        integration_user = fd.update_integration_user_group(integration_user["api_user"],"new_test_group_id")
        self.assertEquals(integration_user["group_id"], "new_test_group_id")
    
    def test_create_group(self):
        fd = TEST_IMPLEMENTATION("test_store")
        group = fd.create_group("test_group_id","test_discord_id","test_integration_user")
        with open(fd.file_stores["group"],'r') as store:
            groups = json.load(store)
        expected = groups["test_group_id"]
        self.assertEqual(expected["id"], group["id"])
    
    def test_get_group(self):
        fd = TEST_IMPLEMENTATION("test_store")
        group = fd.create_group("test_group_id","test_discord_id","test_integration_user")
        expected = fd.get_group("test_group_id")
        self.assertEqual(expected["id"], group["id"])

    def test_update_group(self):
        fd = PersistenceFileDriver("test_store")
        group = fd.create_group("test_group_id","test_discord_id","test_integration_user")
        expected = fd.update_group(group["id"],channel_id="new_test_discord_id")
        self.assertEqual(expected["channel_id"], "new_test_discord_id")
        expected = fd.update_group(group["id"],integration_user_id="new_test_integration_user")
        self.assertEqual(expected["integration_user_id"], "new_test_integration_user")

    def test_create_webhook(self):
        fd = PersistenceFileDriver("test_store")
        webhook = fd.create_webhook("test_user_id","test_webhook_id",WebHook.TASK,WebHook.TASK_OPTIONS)
        with open(fd.file_stores["webhook"],'r') as store:
            webhooks = json.load(store)
        expected = webhooks["test_user_id"]
        self.assertEqual(expected[WebHook.TASK], webhook[WebHook.TASK])

    def test_get_webhook_by_user(self):
        fd = PersistenceFileDriver("test_store")
        webhook = fd.create_webhook("test_user_id","test_webhook_id",WebHook.TASK,WebHook.TASK_OPTIONS)
        expected = fd.get_webhooks_by_user("test_user_id")
        self.assertEqual(expected[WebHook.TASK], webhook[WebHook.TASK])

    def test_get_webhook_by_id(self):
        fd = PersistenceFileDriver("test_store")
        fd.create_webhook("test_user_id","test_webhook_id",WebHook.TASK,WebHook.TASK_OPTIONS)
        expected = fd.get_webhook_by_id("test_webhook_id")
        self.assertEqual(expected['type'], WebHook.TASK)


