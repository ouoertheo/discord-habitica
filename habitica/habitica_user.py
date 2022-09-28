
import asyncio
import config as cfg
import logging
from habitica.habitica_webhook import WebHook
import habitica.habitica_api as api

logger = logging.getLogger(__name__)

class HabiticaUser:
    "Used mainly as a chat integration"
    def __init__(self, api_user, api_token, discord_user_id) -> None:
        self.api_user = api_user
        self.api_token = api_token
        self.discord_user_id = discord_user_id
        self.webhooks: list[WebHook] = []
        self.synced = False
        self.driver = cfg.DRIVER
    
    async def fetch_user_details(self):
        user_json, party_json = await asyncio.gather(
            api.get_user(self.api_user, self.api_token),
            api.get_party(self.api_user, self.api_token)
        )
        self.user_name = user_json["data"]["profile"]["name"]
        self.user_id = user_json["data"]["id"]
        self.group_id = user_json["data"]["party"]["_id"] 
        self.quest = user_json["data"]["party"]["quest"]
        self.group_name = party_json["data"]["name"]
        self.synced = True
        logger.info(f"User {self.user_name} synchronized.")
    
    async def fetch_webhooks(self):
        """
        Fetches webhook configuration from Habitica user to local user if they belong to the local server.
        """
        if not self.synced:
            logger.info(f"Synchronizing user")
            await self.fetch_user_details()
        
        response_json = await api.get_webhooks(self.api_user, self.api_token)

        for webhook_response in response_json["data"]:
            url = webhook_response["url"]
            webhook_type = webhook_response["type"]
            webhook_id = webhook_response["id"]

            if url != cfg.LOCAL_SERVER_URL:
                logger.debug(f"Found webhook {webhook_type} on {url}. Webhook does not match {cfg.LOCAL_SERVER_URL}")
                continue

            self.webhooks.append(WebHook(webhook_type, self.api_user, webhook_id=webhook_id))
            logger.info(f"Adding webhook {webhook_type} on {url}.")
    
    def get_webhook(self, webhook_type=""):
        if webhook_type:
            webhook = [wh for wh in self.webhooks if wh.webhook_type == WebHook.GROUP_CHAT][0]
        if not webhook:
            raise KeyError(f"Webhook {webhook_type} not found")
        return webhook
    
    async def create_webhook(self, webhook: WebHook):
        webhook = await api.create_webhook(self.api_user, self.api_token, webhook.payload)
        return WebHook(webhook['data']['type'])
    
    async def dump(self):
        if not self.synced:
            logger.info(f"Synchronizing user {self.api_user}")
            await self.fetch_user_details()
        self.driver.create_user(
            self.api_user, 
            self.api_token, 
            self.group_id, 
            self.discord_user_id
        )


