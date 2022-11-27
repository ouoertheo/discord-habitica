import discord
from discord.ext import commands
from discord.app_commands import command as app_command
from quart import Quart, request
import asyncio
import json
from habitica.habitica_service import HabiticaService
import config as cfg
import habitica.habitica_webhook as webhook

logger = cfg.logging.getLogger(__name__)

class HabiticaCog(commands.Cog):
    app = Quart(__name__)
    bot: commands.Bot
    
    def __init__(self, bot: commands.Bot) -> None:
        self.habitica = HabiticaService(cfg.DRIVER)
        self.bot = bot
        logger.info("Habitica Cog initialized.")
        asyncio.create_task(self.app.run_task(host="0.0.0.0",port=cfg.SERVER_PORT))
        self.app.add_url_rule("/habitica",view_func=self.habitica_listener, methods=['POST'])

    
    @commands.Cog.listener()
    async def on_ready(self):
        # await self.clear_commands()
        command_list = [
            self.register_user
        ]
        await self.sync_commands(command_list)
        logger.info(f"Habitica Cog loaded and ready")
    
    async def send_message(self, channel_id, content):
        channel = await self.bot.fetch_channel(channel_id)
        response = await channel.send(content)
        return response
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        How am I going to feed the messages/commamnds
        back to Habitica?
        """
        discord_user_id = message.author.id
        try:
            user = self.habitica.get_user(discord_user_id=discord_user_id)
        except Exception as e:
            logger.error(e)
            return

        # Prevent infinite loop when reposting Discord messages to Habitica chat.
        if user.last_message == message.clean_content:
            logger.debug(f"Ignored message {message.clean_content} from {user.user_name} because it was already reposted.")
            return
        user.last_message = message.clean_content
        await user.post_chat(message.clean_content)

    @app_command()
    async def register_user(self, interaction: discord.Interaction, api_user:str, api_token:str):
        discord_user_id = interaction.user.id
        discord_channel_id = interaction.channel_id
        try:
            response = await self.habitica.register_user(api_user, api_token, discord_user_id, discord_channel_id)
            await interaction.response.send_message(f"User {response.user_name} registered with group {response.group_name}")
        except Exception as e:
            await interaction.response.send_message(e)
    
    async def clear_commands(self):
        self.bot.tree.clear_commands(guild=None)
        logger.info("Syncing commands. This could take a while...")
        self.bot.tree.sync()
        logger.info(f"Cleared remote command tree")

    async def sync_commands(self, command_list: list):
        for command in command_list:
            try:
                self.bot.tree.add_command(command)
            except Exception as e:
                logger.error(e)
            logger.info(f"Registered command: {command.name}")
        logger.info("Syncing commands. This could take a while...")
        await self.bot.tree.sync()
        logger.info(f"Synced local command tree")

    @commands.Cog.listener()
    async def on_error(event, *args, **kwargs):
        logger.error(event)

    async def habitica_listener(self):
        """
        Listen for Habitica Webhooks. 
        """
        logger.info(f"{request}")
        req = json.loads(await request.data)
        print(req)
        if "webhookType" in req:
            if req["webhookType"] == "groupChatReceived":
                wh = webhook.GroupChat(req)
                await self.handle_group_chat_webhook(wh)
        else:
            logger.error("Malformed webhook invocation")
        return ""
    
    async def handle_group_chat_webhook(self, wh: webhook.GroupChat):
        if wh.uuid == "system":
            user_name = "System"
        else:
            user_name = wh.username
        user_id = wh.uuid
        group_id = wh.group_id
        message = f"{user_name}: {wh.unformatted_text}"
        last_message = self.habitica.users[user_id].last_message

        # Check if this was just posted to Habitica from Discord
        if wh.unformatted_text == last_message:
            logger.debug(f"Ignored message {wh.unformatted_text} from {user_name} because it was already reposted.")
            return

        if group_id in self.habitica.groups:
            discord_channel_id = self.habitica.groups[wh.group_id].discord_channel_id
        else:
            raise Exception("Received webhook for unregistered group")

        # Send the message and save it to the last message
        self.habitica.users[user_id].last_message = message
        await self.send_message(discord_channel_id, message)
            
def setup(bot):
    bot.load_extension(bot)