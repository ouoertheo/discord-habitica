from habitica.habitica_group import HabiticaGroup
from habitica.habitica_user import HabiticaUser
from habitica.habitica_webhook import WebHook
import habitica.habitica_api as api
import config as cfg
import asyncio

logger = cfg.logging.getLogger(__name__)

class HabiticaService:
    def __init__(self, driver) -> None:
        self.groups: dict[str, HabiticaGroup] = {}
        self.users: dict[str, HabiticaUser] = {}
        self.webhooks: dict[str, WebHook] = {}
        self.load_repo()
    
    def load_repo(self):
        self.load_groups()
        self.load_users()
        for user in self.users.values():
            if user.group_id in self.groups:
                self.groups[user.group_id].add_api_user(user.api_user)
    
    def load_users(self):
        users = cfg.DRIVER.get_all_users()
        for user in users.values():
            api_user = user["api_user"]
            api_token = user["api_token"]
            group_id = user["group_id"]
            discord_user_id = user["discord_id"]
            self.users[api_user] = HabiticaUser(
                api_user, 
                api_token,
                discord_user_id
            )
            self.users[api_user].group_id = group_id
        logger.info("Loaded users")
    
    def load_groups(self):
        groups = cfg.DRIVER.get_all_groups()
        for group in groups.values():
            group_id = group["group_id"]
            api_user = group["api_user"]
            api_token = group["api_token"]
            discord_channel_id = group["discord_channel_id"]
            self.groups[group_id] = HabiticaGroup(
                group_id,
                api_user,
                api_token,
                discord_channel_id,
            )
        logger.info("Loaded groups")

    def get_user(self, api_user="", discord_user_id=""):
        user: HabiticaUser = None
        if api_user:
            user = self.users[api_user]

        if discord_user_id:
            for user in self.users.values():
                if user.discord_user_id == discord_user_id:
                    user = user
        return user

    async def register_user(self, api_user, api_token, discord_user_id, discord_channel_id):
        """
        Create a new user, fetch user details from Habitica API, and add 
        it to a group.

        Will create a new group if it does not exist, setting the user's
        API creds as the group creds.

        Return: New user object
        KeyError: User already exists
        """
        if api_user in self.users:
            raise KeyError(f"Api_user {self.users[api_user].user_name} already registered.")

        user = HabiticaUser(api_user, api_token, discord_user_id)
        try:
            await user.fetch_user_details()
        except:
            pass
        
        if user.group_id in self.groups:
            self.groups[user.group_id].add_api_user(user.user_id)
        else:
            await self.register_group(
                user.group_id,
                api_user,
                api_token,
                discord_channel_id
            )

        self.users[api_user] = user
        await user.dump()
        return user
    
    async def register_group(self, group_id, api_user, api_token, discord_channel_id):
        if group_id in self.groups:
            raise KeyError(f"Group_id {group_id} already exists")
        group = HabiticaGroup(
            group_id,
            api_user,
            api_token,
            discord_channel_id
        )
        self.groups[group_id] = group
        group.dump()

