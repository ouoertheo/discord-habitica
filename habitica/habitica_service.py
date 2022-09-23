from asyncio.log import logger
from habitica.habitica_group import HabiticaGroup
from habitica.habitica_user import HabiticaUser
from habitica.habitica_webhook import WebHook
import habitica_api as api
import config as cfg


class HabiticaService:
    def __init__(self) -> None:
        self.groups: dict[str, HabiticaGroup] = {}
        self.users: dict[str, HabiticaUser] = {}
        self.webhooks: dict[str, WebHook] = {}

    def get_user(self, user_id="", discord_user_id=""):
        user: HabiticaUser = None
        if user_id:
            user = self.users[user_id]

        if discord_user_id:
            discord_ids = {
                user.discord_user_id:user for user in self.users.values() 
                if user.discord_user_id == discord_user_id
            }
            user = discord_ids[discord_user_id]
        return user

    async def register_user(self, api_user, api_token, discord_user_id):
        user = HabiticaUser(api_user, api_token, discord_user_id=discord_user_id)
        await user.fetch_user_details()
        self.users[user.user_id] = user
        self.groups[user.group_id].add_user(user.user_id)
        return user
    
    async def register_group(self, group_id, integration_user_id, discord_channel_id):
        user = self.get_user(user_id=integration_user_id)
        self.groups[group_id] = HabiticaGroup(
            group_id,
            discord_channel_id
        )
        await user.fetch_webhooks()
        try:
            integration_webhook = user.get_webhook(webhook_type=WebHook.GROUP_CHAT)
        except:
            integration_webhook = user.create_webhook(webhook_type=WebHook.GROUP_CHAT)

        self.groups[group_id].integration_user_id = user.user_id


    async def fetch_webhooks(self):
        pass