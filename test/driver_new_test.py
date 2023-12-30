from persistence.file_driver_new import PersistenceFileDriver
from persistence.memory_driver_new import PersistenceMemoryDriver
from persistence.driver_base_new import PersistenceDriverBase
from app.model.app_user import AppUser
from app.app_user_service import AppUserService, AppUserExistsException
from pathlib import Path
import unittest
import os

# Add in class and parameters
TEST_DRIVERS = {
    "file_driver": [PersistenceFileDriver,"test_store"],
    "memory_driver": [PersistenceMemoryDriver]
}
class DriverTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.ephemeral_test_drivers = self.build_test_drivers()
        self.APP_USER_ID = "app_user_id"
        self.APP_USER_NAME = "app_user_name"

    def tearDown(self) -> None:
        self.clear_file_drivers()
    
    def clear_file_drivers(self):
        fd = self.ephemeral_test_drivers["file_driver"]
        for store in fd.store_cache.values():
            if store.exists():
                os.remove(store)

    def build_test_drivers(self):
        "Return a dict of instantiated test drivers"
        test_drivers = {}
        for test_driver in TEST_DRIVERS:
            # The first entry in each TEST_DRIVERS value is the driver, subsequent are params
            # This gets the actual subclass of the ABC object
            drv_class = TEST_DRIVERS[test_driver][0].__mro__[0]
            params = []
            if len(TEST_DRIVERS[test_driver]) > 1:
                params = TEST_DRIVERS[test_driver][1:]

            # Instantiate the drivers
            test_drivers[test_driver] = drv_class(*params)
        return test_drivers

    # Test all drivers
    @unittest.expectedFailure
    async def test_all_drivers(self):
        "Run listed tests on all drivers"
        # Assign tests to run
        tests = [
            self.test_create_and_read_object,
            self.test_delete_object,
            self.test_update_object,
            self.test_list_objects
        ]
        # Run tests for each test driver
        for store in TEST_DRIVERS:
            for test in tests:
                await test(self.ephemeral_test_drivers[store])

    async def test_create_and_read_object(self, driver: PersistenceDriverBase = None):
        if not driver:
            driver = self.ephemeral_test_drivers["file_driver"]
        app_user_service = AppUserService(driver)
        app_user = app_user_service.create_app_user(self.APP_USER_ID, self.APP_USER_NAME)
        app_user_service.add_habitica_user_link(app_user.id,"api_user","api_token","username")
        driver.create(driver.stores.APP_USER, app_user.dump())
        user = driver.read(driver.stores.APP_USER, self.APP_USER_ID)
        self.assertEquals(user["habitica_user_links"][0]["api_user"], "api_user")
    
    async def test_update_object(self, driver: PersistenceDriverBase = None):
        if not driver:
            driver = self.ephemeral_test_drivers["file_driver"]
        app_user_service = AppUserService(driver)
        app_user = app_user_service.create_app_user(self.APP_USER_ID, self.APP_USER_NAME)
        app_user_service.add_habitica_user_link(app_user.id,"api_user","api_token","username")
        driver.create(driver.stores.APP_USER,app_user.dump())
        app_user_service.add_habitica_user_link(app_user.id,"api_user2","api_token2","username2")
        driver.update(driver.stores.APP_USER, app_user.dump())
        user = driver.read(driver.stores.APP_USER, self.APP_USER_ID)
        self.assertEquals(user["habitica_user_links"][1]["api_user"], "api_user2")
        
    async def test_delete_object(self, driver: PersistenceDriverBase = None):
        if not driver:
            driver = self.ephemeral_test_drivers["file_driver"]
        app_user_service = AppUserService(driver)
        
        app_users = app_user_service.get_app_users()
        for app_user in app_users:
            app_user_service.delete_app_user(app_user.id)
            
        app_user = app_user_service.create_app_user(self.APP_USER_ID, self.APP_USER_NAME)

        app_user_service.add_habitica_user_link(app_user.id,"api_user","api_token","username")
        driver.create(driver.stores.APP_USER, app_user.dump())
        user = driver.read(driver.stores.APP_USER, self.APP_USER_ID)
        self.assertEquals(user["habitica_user_links"][0]["api_user"], "api_user")

        driver.delete(driver.stores.APP_USER, self.APP_USER_ID)
        with self.assertRaises(KeyError):
            user = driver.read(driver.stores.APP_USER, self.APP_USER_ID)
    
    async def test_list_objects(self, driver: PersistenceDriverBase = None):
        if not driver:
            driver = self.ephemeral_test_drivers["file_driver"]
        app_user_service = AppUserService(driver)
        app_user = app_user_service.create_app_user(self.APP_USER_ID, self.APP_USER_NAME)
        app_user2 = app_user_service.create_app_user(self.APP_USER_ID+"2", self.APP_USER_NAME+"2")
        app_user_service.add_habitica_user_link(app_user.id,"api_user","api_token","username")
        app_user_service.add_habitica_user_link(app_user2.id,"api_user2","api_token2","username2")
        driver.create(driver.stores.APP_USER, app_user.dump())
        driver.create(driver.stores.APP_USER, app_user2.dump())
        
        app_users_raw = driver.list(driver.stores.APP_USER)
        self.assertEqual(app_users_raw[self.APP_USER_ID]["habitica_user_links"][0]["api_user"], "api_user")
        self.assertEqual(app_users_raw[self.APP_USER_ID+"2"]["habitica_user_links"][0]["api_user"], "api_user2")

