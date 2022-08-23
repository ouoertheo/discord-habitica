
import asyncio
import json
import logging
import logging.config
import os
import sys
from typing import Any
import discord
import dotenv
import aiohttp
from  quart import Quart, request

from registration_cache import RegistrationCache

# Define logger name
with open("logging.json","r") as log_config:
    log_config = json.loads(log_config.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)
app = Quart(__name__)

DISCORD_TOKEN = dotenv.dotenv_values()["DISCORD_TOKEN"]
HABITICA_BASE_URL = dotenv.dotenv_values()["HABITICA_BASE_URL"]
EXTERNAL_SERVER_HOST = dotenv.dotenv_values()["EXTERNAL_SERVER_HOST"]
INTERNAL_SERVER_HOST = dotenv.dotenv_values()["INTERNAL_SERVER_HOST"]
SERVER_PORT = dotenv.dotenv_values()["SERVER_PORT"]

HABITICA_API_USER = dotenv.dotenv_values()["PROXY_HABITICA_USER_ID"]
HABITICA_API_TOKEN = dotenv.dotenv_values()["PROXY_HABITICA_API_TOKEN"]
# HABITICA_API_USER = dotenv.dotenv_values()["TEST_PROXY_HABITICA_USER_ID"]
# HABITICA_API_TOKEN = dotenv.dotenv_values()["TEST_PROXY_HABITICA_API_TOKEN"]



class HabiticaUser:
    def __init__(self, api_user, api_token) -> None:
        self.user = None
        self.server_url = f"http://{EXTERNAL_SERVER_HOST}:{SERVER_PORT}/habitica"
        self.auth_headers = {
            "x-api-user": api_user,
            "x-api-key": api_token
        }

    async def set_user_details(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(HABITICA_BASE_URL+"/user",headers=self.auth_headers) as response:
                response_json = json.loads(await response.text())
                self.user_name = response_json["data"]["profile"]["name"]
                self.user_id = response_json["data"]["id"]
                self.group_id = response_json["data"]["party"]["_id"] 
                self.quest = response_json["data"]["party"]["quest"]
            async with session.get(HABITICA_BASE_URL+"/groups/party",headers=self.auth_headers) as response:
                response_json = json.loads(await response.text())
                self.group_name = response_json["data"]["name"]

    async def verify_webhooks(self):
        if not self.user_name:
            raise Exception("User is not set")
        self.webhooks = {
            "groupChatReceived": False,
            "questActivity": False,
            "taskActivity": False
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(HABITICA_BASE_URL+"/user/webhook",headers=self.auth_headers) as response:
                response_json = json.loads(await response.text())
                for webhook_response in response_json["data"]:
                    webhook = {
                        "id": webhook_response["id"],
                        "url": webhook_response["url"],
                        "type":webhook_response["type"]
                    }
                    url = webhook["url"]
                    if webhook["url"] != self.server_url:
                        logger.error(f"Error: Expected {self.server_url} got {url}")
                    if webhook["type"] == "groupChatReceived":
                        self.webhooks["groupChatReceived"] = True
                    if webhook["type"] == "questActivity":
                        self.webhooks["questActivity"] = True
                    if webhook["type"] == "taskActivity":
                        self.webhooks["taskActivity"] = True
                
                if not self.webhooks["groupChatReceived"]:
                    logger.info("groupChatReceived webhook not found, creating...")
                    await self.create_groupChatReceived_webhook(self.group_id)
                
                if not self.webhooks["taskActivity"]:
                    logger.info("taskActivity webhook not found, creating...")
                    await self.create_taskActivity_webhook()
                return self.webhooks

    async def create_groupChatReceived_webhook(self, group_id):
        payload = {
            "enabled": True,
            "url": self.server_url,
            "label": "Discord Habitica Chat Webhook",
            "type": "groupChatReceived",
            "options": {
                "groupId": group_id
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                HABITICA_BASE_URL+"/user/webhook",
                headers=self.auth_headers,
                json=payload
            ) as response:
                if response.status >= 400:
                    raise Exception("Failed to create groupChatReceived webhook")
                return True

    async def create_taskActivity_webhook(self):
        payload = {
            "enabled": True,
            "url": self.server_url,
            "label": "Discord Habitica Task Activity Webhook",
            "type": "taskActivity",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                HABITICA_BASE_URL+"/user/webhook",
                headers=self.auth_headers,
                json=payload
            ) as response:
                if response.status >= 400:
                    raise Exception("Failed to create groupChatReceived webhook")
                return True
    
class HabiticaBot(discord.Client):
    def __init__(self, **options: Any) -> None:

        self.habitica_user: HabiticaUser = None
        self.channel = None
        self.cache = RegistrationCache()
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, **options)

    async def on_ready(self):
        logger.info("Discord client ready. Intializing Habitica connection...")
        self.habitica_user = HabiticaUser(HABITICA_API_USER, HABITICA_API_TOKEN)
        await self.habitica_user.set_user_details()
        await self.habitica_user.verify_webhooks()
        logger.info(f"Bot connected to Habitica using user: {self.habitica_user.user_name}")
        logger.info(f"Available webhooks: {self.habitica_user.webhooks}")
        
    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if message.content.startswith(".register"):
            async with message.channel.typing():
                registration_result = self.register_channel_command(message.clean_content, message.channel.id)
                await message.channel.send(registration_result)
    
    def register_channel_command(self, message: str, channel_id: str):
        try:
            group_id = message.split()[1]
        except Exception:
            return ".register requires group_id argument"
        if self.channel:
            return f"Already registered habitica group_id: {group_id}"
        else:
            try:
                self.channel = self.cache.get_channel(group_id)
                return f"Already registered habitica group_id: {group_id}"
            except KeyError:
                self.cache.save_channel(channel_id, group_id)
                return f"Registered habitica group_id: {self.habitica_user.group_id}"
    
    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        logger.exception(sys.exc_info())
        raise Exception(sys.exc_info())

    
    async def handle_groupChatReceived(self, payload):
        try:
            if payload["chat"]["uuid"] == "system":
                user_name = "System"
            else:
                user_name = payload["chat"]["username"]
            user_id = payload["chat"]["uuid"]
            group_id = payload["chat"]["groupId"]
            message = payload["chat"]["unformattedText"]

            if not self.channel:
                channel_id = self.cache.get_channel(group_id)
                self.channel = self.get_channel(channel_id)

            if self.habitica_user.group_id == group_id:
                async with self.channel.typing():
                    logger.debug(f"Sent message:\"{user_name}: {message}\"")
                    await self.channel.send(f"{user_name}: {message}")
        except Exception as err:
            logger.error(err)

    def register_channel(self, channel_id, group_id):
        """
        Checks REGISTERED_CHANNELS cache for existing group:channel mapping. If its not there, create it.
        returns: channel that is registered
        """
        cache: dict[str,str]
        self.channel = self.get_channel(channel_id)
        group_id = self.habitica_user.group_id


bot = HabiticaBot()

@app.route("/habitica", methods=['POST'])
async def habitica_listener():
    webhook_json = json.loads(await request.data)
    if "webhookType" in webhook_json:
        if webhook_json["webhookType"] == "groupChatReceived":
            logger.debug(webhook_json)
            await bot.handle_groupChatReceived(webhook_json)
    else:
        logger.error("Malformed webhook invocation")
    return ""

async def main():
    await asyncio.gather(
        bot.start(DISCORD_TOKEN),
        app.run_task(host=INTERNAL_SERVER_HOST,port=SERVER_PORT)
    )

if __name__ == "__main__":
    asyncio.run(main())
