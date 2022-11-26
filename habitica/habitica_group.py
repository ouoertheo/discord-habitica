from habitica.habitica_webhook import WebHook
import habitica.habitica_api as api
import config as cfg
import asyncio

logger = cfg.logging.getLogger(__name__)
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

        asyncio.create_task(self.sync_webhooks())

    def add_api_user(self, api_user):
        self.api_users.add(api_user)

    
    async def sync_webhooks(self):
        for webhook in self.webhooks:
            url = cfg.LOCAL_SERVER_URL
            habitica_webhooks = await api.get_webhooks(self.api_user, self.api_token)
            for habitica_webhook in habitica_webhooks['data']:
                webhook_type = habitica_webhook["type"]
                webhook_url = habitica_webhook["url"]
                if webhook.webhook_type == webhook_type:
                    if webhook_url == url:
                        logger.debug(f"Group webhook type {webhook.webhook_type} exists on group_id {self.group_id}")
                await api.create_webhook(self.api_user, self.api_token, webhook.payload)

    def dump(self):
        cfg.DRIVER.create_group(
            self.group_id,
            self.api_user,
            self.api_token,
            self.discord_channel_id
        )

