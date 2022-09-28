from asyncio.log import logger
from habitica.habitica_group import HabiticaGroup
from habitica.habitica_user import HabiticaUser
from habitica.habitica_webhook import WebHook
import habitica_api as api
import config as cfg


class HabiticaService:
    def __init__(self, driver) -> None:
        self.groups: dict[str, HabiticaGroup] = {}
        self.users: dict[str, HabiticaUser] = {}
        self.webhooks: dict[str, WebHook] = {}
    
    def load_users(self):
        users = cfg.DRIVER.get_all_users()
        for user in users:
            api_user = user["api_user"]
            api_token = user["api_token"]
            group_id = user["group_id"]
            discord_user_id = user["discord_user_id"]
            self.users[api_user] = HabiticaUser(
                api_user, 
                api_token,
                group_id,
                discord_user_id
            )
    
    def load_groups(self):
        groups = cfg.DRIVER.get_all_groups()
        for group in groups.values():
            group_id = group["group_id"]
            api_user = group["api_user"]
            api_token = group["api_token"]
            api_users = group["api_users"]
            discord_channel_id = group["discord_channel_id"]
            self.groups[group_id] = HabiticaGroup(
                group_id,
                api_user,
                api_token,
                api_users,
                discord_channel_id,
            )

    def get_user(self, api_user="", discord_user_id=""):
        user: HabiticaUser = None
        if api_user:
            user = self.users[api_user]

        if discord_user_id:
            for user in self.users:
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
        if self.users[api_user]:
            raise KeyError(f"UserApi_user {api_user} registered")

        user = HabiticaUser(api_user, api_token, discord_user_id)
        try:
            await user.fetch_user_details()
        except:
            pass
        
        if user.group_id in self.groups:
            self.groups[user.group_id].add_api_user(user.user_id)
        else:
            self.register_group(
                user.group_id,
                api_user,
                api_token,
                discord_channel_id
            )

        self.users[api_user] = user
        user.dump()
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
        for webhook in group.webhooks:
            try:
                await self.sync_webhook(api_user, api_token, webhook)
            except KeyError:
                continue
        self.groups[group_id] = group
        group.dump()

    async def sync_webhook(self, api_user, api_token, webhook: WebHook):
        url = cfg.LOCAL_SERVER_URL
        habitica_webhooks = await api.get_webhooks(api_user, api_token)
        for habitica_webhook in habitica_webhooks:
            webhook_type = habitica_webhook["data"]["type"]
            webhook_url = habitica_webhook["data"]["url"]
            if webhook == webhook_type:
                if webhook_url == cfg.LOCAL_SERVER_URL:
                    raise KeyError(f"{webhook.webhook_type} exists on api_user {api_user}")
            await api.create_webhook(api_user, api_token, webhook.payload)

svc = HabiticaService(cfg.DRIVER)