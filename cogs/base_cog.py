import discord
from discord.ext import commands
from discord.app_commands import command as app_command

from loguru import logger

import cogs.command_sync as command_sync

class BaseCog(commands.Cog):
    def __init__(self, bot: commands.bot) -> None:
        self.bot = bot
        self.app_commands = []
        self.ready = False
        logger.info(f"Initializing {self.__cog_name__} Cog...")
    
    
    @commands.Cog.listener()
    async def on_ready(self):
        command_sync.command_list += self.app_commands
        await command_sync.sync_commands(self.bot)
        logger.info(f"{self.__cog_name__} Cog loaded and ready")
        self.ready = True
    
    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        logger.error(f"Error in cog {self.__cog_name__} in {event}")