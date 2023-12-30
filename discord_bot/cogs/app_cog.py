import asyncio
from discord.ext import commands
from app.app_service import AppService
from app.events.event_service import post_event
from app.events.app_events import SendAccountStatus

from loguru import logger

class AppUserCog(commands.Cog):
    def __init__(self, bot: commands.Bot, app_service: AppService) -> None:
        self.bot = bot
        self.app_commands = [self.register_user]
        self.app_service = app_service
        logger.info("AppUser Cog initialized.")
    
    @commands.hybrid_group(name="user")
    async def app_user_commands(self, ctx: commands.Context[commands.Bot]) -> None:
        pass
    
    @app_user_commands.command(name="register_user")
    async def register_user(self, ctx: commands.Context[commands.Bot], api_user:str, api_token:str):
        discord_user_id = str(ctx.interaction.user.id)
        discord_channel_id = str(ctx.interaction.channel_id)
        discord_user_name = ctx.interaction.user.name
        logger.info(f"Recieved registration command. discord_user_id: {discord_user_id}, discord_user_name: {discord_user_name}, discord_channel_id: {discord_channel_id}, api_user: {api_user}")
        try:
            await self.app_service.register_habitica_account(discord_user_id, discord_user_name, discord_channel_id, api_user, api_token)
            await ctx.interaction.response.send_message(f"User {discord_user_name} registered successfully.")
        except Exception as e:
            await ctx.interaction.response.send_message(str(e))

    @app_user_commands.command(name="get_status")
    async def send_account_status(self, ctx: commands.Context[commands.Bot]):
        asyncio.create_task(post_event(SendAccountStatus(ctx.author.id, ctx.channel.id, ctx.interaction)))