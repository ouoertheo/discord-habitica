import config as cfg

import discord
from discord.ext import commands
from discord.app_commands import command as app_command

import asyncio
import json

from habitica.habitica_service import HabiticaService
import habitica.habitica_wekbhooks as webhook

logger = cfg.logging.getLogger(__name__)

class HabiticaCog(commands.Cog):
    bot: commands.Bot
    def __init__(self, bot: commands.Bot) -> None:
        self.habitica = HabiticaService(cfg.DRIVER)
        self.bot = bot

    async def handle_group_chat_webhook(self, wh: webhook.GroupChat):
        '''
        Repost group chat messages from Habitica to Discord
        '''
        if wh.uuid == "system":
            user_name = "System"
        else:
            user_name = wh.username
        user_id = wh.uuid
        group_id = wh.group_id
        message = f"{user_name}: {wh.unformatted_text}"

        # Warn if a group chat webhook is received for an unregistered group
        if group_id in self.habitica.groups:
            discord_channel_id = self.habitica.groups[wh.group_id].discord_channel_id
        else:
            logger.warning("Received webhook for unregistered group")

        # Check if this was just posted to Habitica from Discord
        last_message = self.habitica.users[user_id].last_message
        if wh.unformatted_text == last_message:
            logger.debug(f"Ignored message {wh.unformatted_text} from {user_name} because it was already reposted.")
            return

        # Send the message and save it to the last message
        self.habitica.users[user_id].last_message = message
        await self.send_message(discord_channel_id, message)