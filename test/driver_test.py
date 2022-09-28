from persistence.file_driver import PersistenceFileDriver 
from habitica.habitica_webhook import WebHook
import unittest
import os
import json

TEST_STORE = "test_store"
TEST_IMPLEMENTATION = PersistenceFileDriver
class DriverTest(unittest.TestCase):

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
        fd.create_user("api_user","api_token","group_id","discord_user_id")
        user = fd.get_user("api_user")
        self.assertEquals(user["api_user"], "api_user")

    def test_get_user(self):
        fd = TEST_IMPLEMENTATION("test_store")
        fd.create_user("api_user","api_token","group_id","discord_user_id")
        user = fd.get_user("api_user")
        self.assertEquals(user["api_user"], "api_user")
    
    def test_update_user_group(self):
        fd = TEST_IMPLEMENTATION("test_store")
        fd.create_user("api_user","api_token","group_id","discord_user_id")
        user = fd.get_user("api_user")
        user = fd.update_user_group(user["api_user"],"new_test_group_id")
        self.assertEquals(user["group_id"], "new_test_group_id")

    def test_create_group(self):
        fd = TEST_IMPLEMENTATION("test_store")
        group = fd.create_group("group_id","api_user","api_token","discord_channel_id","api_users")
        expected = fd.get_group("group_id")
        self.assertEqual(expected["group_id"], group["group_id"])
    
    def test_get_group(self):
        fd = TEST_IMPLEMENTATION("test_store")
        group = fd.create_group("group_id","api_user","api_token","discord_channel_id","api_users")
        expected = fd.get_group("group_id")
        self.assertEqual(expected["group_id"], group["group_id"])

    def test_update_group(self):
        fd = PersistenceFileDriver("test_store")
        group = fd.create_group("group_id","api_user","api_token","discord_channel_id","api_users")
        expected = fd.update_group_api_creds(group["group_id"],"api_user_new","api_token_new")
        self.assertEqual(expected["api_user"], "api_user_new")
        expected = fd.update_group_channel(group["group_id"],"discord_channel_id_new")
        self.assertEqual(expected["discord_channel_id"], "discord_channel_id_new")


