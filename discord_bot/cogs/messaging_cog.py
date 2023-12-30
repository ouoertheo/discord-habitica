import discord
from discord.ext import commands
from discord.app_commands import command as app_command

from loguru import logger

from habitica.habitica_service import HabiticaUser
import app.events.event_service as event_service
from app.events import discord_events


class MessagingCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        event_service.subscribe(discord_events.SendDiscordMessage.type, self.handle_send_message_event)
        logger.info("Discord Messaging Cog initialized.")
    
    async def handle_send_message_event(self, event: discord_events.SendDiscordMessage):
        """Handle SendDiscordMessage events and send them to specified location"""
        channel = self.bot.get_channel(event.discord_channel) if hasattr(event,"discord_channel") else None
        user = self.bot.get_user(event.discord_user_id) if hasattr(event,"discord_user_id") else None
        interaction: discord.Interaction = getattr(event,"interaction", None)

        # Only send message to one of the specified methods
        if channel:
            await channel.send(event.message)
            logger.info(f"Sent message to channel {channel.name}")
        elif user:
            if user.dm_channel:
                await user.dm_channel.send(event.message)
                logger.info(f"Sent DM message to user {user.name}")
            else:
                logger.info(f"Creating DM channel with {user.name}")
                dm_channel = await user.create_dm()
                await dm_channel.send(event.message)
                logger.info(f"Sent DM message to {user.name}")
        elif interaction:
            try:
                await interaction.response.send_message(event.message, ephemeral=event.ephemeral)
                logger.info(f"Sent interaction message to channel {interaction.channel.name}")
            except discord.errors.HTTPException as e:
                dm_channel = interaction.user.dm_channel
                if not dm_channel:
                    dm_channel = await interaction.user.create_dm()
                await dm_channel.send(event.message)
                logger.warning(f"Problem with responding to interaction. DM'd user {interaction.channel.name}. Exception: {str(e)}")
    
    # Listen for any messages in channels that the bot is present in.
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Bot handler for messages typed into Discord
        """
        if self.bot.user.id != message.author.id:
            await event_service.post_event(discord_events.ReceiveDiscordMessage(message))

    async def handle_group_chat_webhook(self, wh):
        '''
        Repost group chats to the the Discord channel. 
        '''
        pass
    
    async def repost_message(self, message, from_discord: bool, habitica_user: HabiticaUser, discord_channel_id=""):
        '''
        Reposts a message to either Discord or Habitica depending on source

        from_discord: True if message originates from Discord. False if from Habitica chat
        discord_channel_id: required when from_discord         
        ''' 
        # last_message = habitica_user.last_message
        # if message == last_message:
        #     logger.debug(f"Ignored message {message} from {habitica_user.user_name} because it was already reposted.")
        #     return
        # habitica_user.last_message = message
        # if from_discord:
        #     await habitica_user.post_chat(message)
        # else:
        #     asyncio.create_task(event.post_event(event.SendDiscordMessage(discord_channel_id, message)))
        pass
