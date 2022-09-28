import asyncio
import json
import logging
import logging.config
import sys
from typing import Any
import discord
from discord.app_commands import command
from discord.ext import commands
from discord import ui
import aiohttp
from quart import Quart, request
from registration_cache import RegistrationCache
import config as cfg

# Define logger name
with open("logging.json","r") as log_config:
    log_config = json.loads(log_config.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)
app = Quart(__name__)


class Questionnaire(ui.Modal, title='Habitica User Registration'):
    api_user = ui.TextInput(label='API User')
    api_key = ui.TextInput(label='API Key')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your response, {self.name}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        return await super().on_error(interaction, error)()


class HabiticaUser:
    def __init__(self, api_user, api_token) -> None:
        self.user = None
        self.local_server_url = f"{cfg.EXTERNAL_SERVER_URL}:{cfg.EXTERNAL_SERVER_PORT}/habitica"
        self.auth_headers = {
            "x-api-user": api_user,
            "x-api-key": api_token
        }

    async def set_user_details(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(cfg.HABITICA_API_BASE_URL+"/user",headers=self.auth_headers) as response:
                response_json = json.loads(await response.text())
                self.user_name = response_json["data"]["profile"]["name"]
                self.user_id = response_json["data"]["id"]
                self.group_id = response_json["data"]["party"]["_id"] 
                self.quest = response_json["data"]["party"]["quest"]
            async with session.get(cfg.HABITICA_API_BASE_URL+"/groups/party",headers=self.auth_headers) as response:
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
            async with session.get(cfg.HABITICA_API_BASE_URL+"/user/webhook",headers=self.auth_headers) as response:
                response_json = json.loads(await response.text())
                for webhook_response in response_json["data"]:
                    webhook = {
                        "id": webhook_response["id"],
                        "url": webhook_response["url"],
                        "type":webhook_response["type"]
                    }
                    url = webhook["url"]
                    if webhook["url"] == self.local_server_url:
                        if webhook["type"] == "groupChatReceived":
                            self.webhooks["groupChatReceived"] = True
                            logger.info(f"Found webhook groupChatReceived on {self.local_server_url}")
                        if webhook["type"] == "questActivity":
                            self.webhooks["questActivity"] = True
                            logger.info(f"Found webhook questActivity on {self.local_server_url}")
                        if webhook["type"] == "taskActivity":
                            self.webhooks["taskActivity"] = True
                            logger.info(f"Found webhook taskActivity on {self.local_server_url}")
                    else:
                        logger.warn(f"Looking for {self.local_server_url} found {url}")
                
                if not self.webhooks["groupChatReceived"]:
                    logger.info(f"groupChatReceived webhook not found, creating on {self.local_server_url}")
                    await self.create_groupChatReceived_webhook(self.group_id)
                
                if not self.webhooks["taskActivity"]:
                    logger.info(f"taskActivity webhook not found, creating on {self.local_server_url}")
                    await self.create_taskActivity_webhook()
                return self.webhooks

    async def create_groupChatReceived_webhook(self, group_id):
        payload = {
            "enabled": True,
            "url": self.local_server_url,
            "label": "Discord Habitica Chat Webhook",
            "type": "groupChatReceived",
            "options": {
                "groupId": group_id
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                cfg.HABITICA_API_BASE_URL+"/user/webhook",
                headers=self.auth_headers,
                json=payload
            ) as response:
                if response.status >= 400:
                    raise Exception("Failed to create groupChatReceived webhook")
                return True

    async def create_taskActivity_webhook(self):
        payload = {
            "enabled": True,
            "url": self.local_server_url,
            "label": "Discord Habitica Task Activity Webhook",
            "type": "taskActivity",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                cfg.HABITICA_API_BASE_URL+"/user/webhook",
                headers=self.auth_headers,
                json=payload
            ) as response:
                if response.status >= 400:
                    raise Exception("Failed to create groupChatReceived webhook")
                return True
    
class HabiticaBot(commands.Bot):
    def __init__(self, **options: Any) -> None:
        self.my_bot = self
        self.habitica_user: HabiticaUser = None
        self.channel = None
        self.cache = RegistrationCache()
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(".", intents=intents, **options)

    async def on_ready(self):
        logger.info("Discord client ready. Intializing Habitica connection...")
        self.habitica_user = HabiticaUser(cfg.HABITICA_API_USER, cfg.HABITICA_API_TOKEN)
        await self.habitica_user.set_user_details()
        await self.habitica_user.verify_webhooks()
        logger.info(f"Bot connected to Habitica using user: {self.habitica_user.user_name}")
        logger.info(f"Available webhooks: {self.habitica_user.webhooks}")
        
    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        await self.process_commands(message)
        if message.content.startswith(".register"):
            async with message.channel.typing():
                registration_result = self.register_channel_command(message.clean_content, message.channel.id)
                await message.channel.send(registration_result)
        # if message.content == ".test":
        #     await message.channel.send("Hello World", components=[
        #         Button(style=discord.ButtonStyle.primary, label="Press me", custom_id="my_custom_id")
        #     ])
    
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

    
    async def handle_webhook(self, payload):
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

    async def on_interaction(self, interaction: discord.Interaction):
        pass

    async def setup_hook(self) -> None:
        # Sync the application command with Discord.
        self.tree.add_command(self.test_command)
        await self.tree.sync()


    @command()
    async def test_command(self, interaction: discord.Interaction, potato:str, bacon:str):
        print(f"{potato} {bacon}")
        await interaction.response.send_message("Ok!")

bot = HabiticaBot()

@app.route("/habitica", methods=['POST'])
async def habitica_listener():
    webhook_json = json.loads(await request.data)
    if "webhookType" in webhook_json:
        if webhook_json["webhookType"] == "groupChatReceived": # TODO: Generalize this better
            logger.debug(webhook_json)
            await bot.handle_webhook(webhook_json)
    else:
        logger.error("Malformed webhook invocation")
    return ""

async def main():
    await asyncio.gather(
        bot.start(cfg.DISCORD_TOKEN),
        app.run_task(host="0.0.0.0",port=cfg.SERVER_PORT)
    )

@bot.tree.command()
async def register_party(interaction: discord.Interaction, habitica_guild_id: str):
    bot.register_channel(interaction.channel_id, habitica_guild_id)

@bot.tree.command()
async def register_user(interaction: discord.Interaction):
    await interaction.response.send_modal(Questionnaire())

if __name__ == "__main__":
    asyncio.run(main())
