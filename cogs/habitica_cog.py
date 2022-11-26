import discord
from discord.ext import commands
from discord.app_commands import command as app_command
from quart import Quart, request
import asyncio
import json
from habitica.habitica_service import habitica
import config as cfg

logger = cfg.logging.getLogger(__name__)

class HabiticaCog(commands.Cog):
    app = Quart(__name__)
    bot: commands.Bot
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        logger.info("Habitica Cog initialized.")
        asyncio.create_task(self.app.run_task(host="0.0.0.0",port=cfg.SERVER_PORT))

    
    @commands.Cog.listener()
    async def on_ready(self):
        # await self.clear_commands()
        command_list = [
            self.register_user
        ]
        await self.sync_commands(command_list)
        logger.info(f"Habitica Cog loaded and ready")
    
    async def send_message(self, channel_id, content):
        channel = self.bot.fetch_channel(channel_id)
        await channel.send(content)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        How am I going to feed the messages/commamnds
        back to Habitica?
        """
        print(message)
        
    @app_command()
    async def test_command(self, interaction: discord.Interaction, arg1:str, arg2:str):
        print(f"{arg1} {arg2}")
        await interaction.response.send_message("Ok!")
    
    @app_command()
    async def register_user(self, interaction: discord.Interaction, api_user:str, api_token:str):
        discord_user_id = interaction.user.id
        discord_channel_id = interaction.channel_id
        try:
            response = await habitica.register_user(api_user, api_token, discord_user_id, discord_channel_id)
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

    @app.route("/habitica", methods=['POST'])
    async def habitica_listener(self):
        """
        Listen for Habitica Webhooks. 
        # """
        logger.info(f"{request}")
        req = json.loads(await request.data)

        if "webhookType" in req:
            if req["webhookType"] == "groupChatReceived":
                logger.debug(req)
                
                await self.bot.handle_webhook(req)
        else:
            logger.error("Malformed webhook invocation")
        return ""
    
    
    

def setup(bot):
    bot.load_extension(bot)