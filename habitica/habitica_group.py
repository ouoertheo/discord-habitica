from habitica.habitica_webhook import WebHook
from habitica_user import HabiticaUser

class HabiticaGroup:
    def __init__(self, group_id, discord_channel_id) -> None:
        self.group_id = group_id
        self.user_member_ids: set[str] = {}
        self.discord_channel_id = discord_channel_id
        self.integration_user_id = None

    def add_user(self, user_id):
        self.user_member_ids.add(user_id)

    async def set_integration_user_id(self, user_id):
        if user_id not in self.user_member_ids:
            raise ValueError(f"user_id {user_id} does not exist in group users")

        self.integration_webhook = WebHook(WebHook.GROUP_CHAT,user_id)
        self.integration_webhook.GROUP_CHAT_OPTIONS["groupId"] = self.group_id


        await self.users[user_id].create_webhook(self.integration_webhook)
        self.integration_user_id = user_id

    
        


