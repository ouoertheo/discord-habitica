from habitica.habitica_webhook import WebHook
import config as cfg
class HabiticaGroup:
    def __init__(self, group_id, api_user, api_token, discord_channel_id) -> None:
        self.group_id = group_id
        self.api_user = api_user
        self.api_token = api_token
        self.api_users: set[str] = {}
        self.discord_channel_id = discord_channel_id
        
        self.chat_webhook = WebHook(WebHook.GROUP_CHAT, api_user)
        self.chat_webhook.GROUP_CHAT_OPTIONS["groupId"] = self.group_id

        self.webhooks = [
            self.chat_webhook
        ]

    def add_api_user(self, api_user):
        self.api_users.add(api_user)

    def dump(self):
        cfg.DRIVER.create_group(
            self.group_id,
            self.api_user,
            self.api_token,
            self.discord_channel_id
        )

