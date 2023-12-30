import unittest
from app.app_user_service import AppUserService, AppUserExistsException, HabiticaUserLinkExists, AppUserNotFoundException, HabiticaUserLink
from app.model.app_user import AppUser
from persistence.memory_driver_new import PersistenceMemoryDriver

class AppUserServiceTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.driver = PersistenceMemoryDriver()
        self.app_user_service = AppUserService(self.driver)
        self.HABITICA_API_USER = "TEST_USER"
        self.HABITICA_API_TOKEN = "TEST_TOKEN"
        self.HABITICA_USER_NAME = "TEST_USER_NAME"
        self.APP_USER_ID = "app_user_id"
        self.APP_USER_NAME = "app_user_name"

    def test_init_store(self):
        app_user_service = self.app_user_service
        app_user = app_user_service.create_app_user(self.APP_USER_ID, self.APP_USER_NAME)
        self.app_user_service.add_habitica_user_link(app_user.id, self.HABITICA_API_USER, self.HABITICA_API_TOKEN, self.HABITICA_USER_NAME)

        # Passing the same driver (memory driver) back to new app.
        app2 = AppUserService(self.driver)
        self.assertTrue(app2.get_app_user(app_user_id=self.APP_USER_ID).id, self.APP_USER_ID)
        self.assertTrue(app2.get_habitica_user_link(app_user_id=self.APP_USER_ID).api_user, self.HABITICA_API_USER)
        self.assertTrue(app2.get_habitica_user_link(app_user_id=self.APP_USER_ID).api_token, self.HABITICA_API_TOKEN)

    def test_create_app_user(self):
        app = self.app_user_service
        app.create_app_user(self.APP_USER_ID, self.APP_USER_NAME)
        self.assertTrue(app.get_app_user(app_user_id=self.APP_USER_ID).id, self.APP_USER_ID)
        with self.assertRaises(AppUserExistsException):
            app.create_app_user(self.APP_USER_ID, self.APP_USER_NAME)
    
    def test_get_app_user(self):
        app = self.app_user_service
        app.create_app_user(self.APP_USER_ID, self.APP_USER_NAME)
        app.create_app_user(self.APP_USER_ID+"2", self.APP_USER_NAME+"2")

        self.assertTrue(app.get_app_user(app_user_id=self.APP_USER_ID).id, self.APP_USER_ID)

    def test_delete_app_user(self):
        app = self.app_user_service

        app.create_app_user(self.APP_USER_ID, self.APP_USER_NAME)
        self.assertTrue(app.get_app_user(app_user_id=self.APP_USER_ID).id, self.APP_USER_ID)

        app.delete_app_user(self.APP_USER_ID)
        with self.assertRaises(AppUserNotFoundException):
            app.delete_app_user(self.APP_USER_ID)

    async def test_add_habitica_user_link(self):
        app = self.app_user_service
        app_user = app.create_app_user(self.APP_USER_ID, self.APP_USER_NAME)
        self.app_user_service.add_habitica_user_link(app_user.id, self.HABITICA_API_USER, self.HABITICA_API_TOKEN, self.HABITICA_USER_NAME)
        self.assertEqual(app_user.habitica_user_links[0].api_user, "TEST_USER")

        # Test HabiticaUserLinkExists exception, do not allow the same Habitica User to be registered more than once
        with self.assertRaises(HabiticaUserLinkExists):
            self.app_user_service.add_habitica_user_link(app_user.id, self.HABITICA_API_USER, self.HABITICA_API_TOKEN, self.HABITICA_USER_NAME)

    async def test_get_habitica_user_links(self):
        app = self.app_user_service
        app_user1 = app.create_app_user(self.APP_USER_ID+"1", self.APP_USER_NAME+"1")
        app_user2 = app.create_app_user(self.APP_USER_ID+"2", self.APP_USER_NAME+"2")
        app_user3 = app.create_app_user(self.APP_USER_ID+"3", self.APP_USER_NAME+"3")

        # Add two Habitica Users to app
        link1a = self.app_user_service.add_habitica_user_link(app_user1.id, self.HABITICA_API_USER+"1a", self.HABITICA_API_TOKEN+"1a", self.HABITICA_USER_NAME+"1a")
        self.app_user_service.add_habitica_user_link(app_user1.id, self.HABITICA_API_USER+"1b", self.HABITICA_API_TOKEN+"1b", self.HABITICA_USER_NAME+"1b")
        
        # Add one Habitica User to app_user 2 and 3
        self.app_user_service.add_habitica_user_link(app_user2.id, self.HABITICA_API_USER+"2", self.HABITICA_API_TOKEN+"2", self.HABITICA_USER_NAME+"2")
        self.app_user_service.add_habitica_user_link(app_user3.id, self.HABITICA_API_USER+"3", self.HABITICA_API_TOKEN+"3", self.HABITICA_USER_NAME+"3")

        # Test getting all users
        users = self.app_user_service.get_habitica_user_links()
        self.assertEqual(len(users), 4)
        self.assertTrue(all([type(user) == HabiticaUserLink for user in users])) # Make sure we have the right objects

        # Test getting all users from app_user1
        users = self.app_user_service.get_habitica_user_links(app_user_id=app_user1.id)
        self.assertEqual(len(users), 2)

        # Test getting single user by id
        user = self.app_user_service.get_habitica_user_link(habitica_user_id=self.HABITICA_API_USER+"1a")
        self.assertEqual(user.api_token, link1a.api_token)


    # NOT IMPLEMENTED YET
    # async def test_get_user_map(self):
    #     app = self.app_user_service
    #     app_user = self.app_user_service.create_app_user("discord_user")
    #     app.add_habitica_user_link( app_user.id, "discord_channel", self.HABITICA_API_USER, self.HABITICA_API_TOKEN)

    #     # Test getting by discord and api_user
    #     self.assertEqual(app.get_user_map(app_user.id,api_user=self.HABITICA_API_USER).api_user, self.HABITICA_API_USER)
    #     self.assertEqual(app.get_user_map(app_user.id, discord_channel="discord_channel").discord_channel, "discord_channel")


