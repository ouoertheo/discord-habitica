import discord
from discord.ext import commands
from discord.app_commands import command as app_command
from app.app_service import AppService
from app.events import discord_events, event_service
from cogs.base_cog import BaseCog

from loguru import logger

class AppCog(BaseCog):
    def __init__(self, bot: commands.bot, app_service: AppService) -> None:
        super().__init__(bot)
        self.app_commands = [self.register_user]
        self.app_service = app_service
        logger.info("Bank Cog initialized.")
    
    @app_command()
    async def register_user(self, interaction: discord.Interaction, api_user:str, api_token:str):
        discord_user_id = interaction.user.id
        discord_channel_id = interaction.channel_id
        logger.info(f"Recieved registration command. discord_user_id: {discord_user_id}, discord_channel_id: {discord_channel_id}, api_user: {api_user}")
        try:
            await self.app_service.register_habitica_account(str(discord_user_id), str(discord_channel_id), api_user, api_token)
            await interaction.response.send_message(f"User registered successfully.")
        except Exception as e:
            await interaction.response.send_message(str(e))

def setup(bot):
    bot.load_extension(bot)