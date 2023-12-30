import datetime
import os
import traceback
import typing
from loguru import logger

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

from discord_bot.cogs import app_cog, bank_cog, messaging_cog
from app.app_service import AppService


class DiscordHabiticaBot(commands.Bot):
    client: aiohttp.ClientSession
    _uptime: datetime.datetime = datetime.datetime.utcnow()

    def __init__(self, prefix: str, ext_dir: str, app_service: AppService, *args: typing.Any, **kwargs: typing.Any) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(*args, **kwargs, command_prefix=commands.when_mentioned_or(prefix), intents=intents)
        self.logger = logger
        self.ext_dir = ext_dir
        self.app_service = app_service

    async def _load_extensions(self) -> None:
        await self.add_cog(app_cog.AppUserCog(self, self.app_service))
        await self.add_cog(bank_cog.BankCog(self, self.app_service.bank_service, self.app_service.app_user_service, self.app_service.habitica_service))
        await self.add_cog(messaging_cog.MessagingCog(self))

    async def on_error(self, event_method: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.logger.error(f"An error occurred in {event_method}.\n{traceback.format_exc()}")

    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user} ({self.user.id})")

    async def setup_hook(self) -> None:
        self.client = aiohttp.ClientSession()
        self.logger.info("Loading Cogs...")
        await self._load_extensions()
        self.logger.info("Syncing command tree...")
        commands = await self.tree.sync()
        self.logger.info(f"Command tree synced. Synced commands: {[command.name for command in commands]}")

    async def close(self) -> None:
        await super().close()
        await self.client.close()
    
    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        """Sync commands"""
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands globally")


    def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        load_dotenv()
        try:
            super().run(str(os.getenv("TOKEN")), *args, **kwargs)
        except (discord.LoginFailure, KeyboardInterrupt):
            self.logger.info("Discord bot exiting...")
            exit()

    @property
    def user(self) -> discord.ClientUser:
        assert super().user, "Bot is not ready yet"
        return typing.cast(discord.ClientUser, super().user)

    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.utcnow() - self._uptime
