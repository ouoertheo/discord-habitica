import discord
from discord.ext import commands
from discord.app_commands import command as app_command

from loguru import logger

from habitica.habitica_service import HabiticaUser
import app.events.event_service as event_service
from app.events import discord_events, bank_events, app_events
import cogs.command_sync as command_sync
from cogs.base_cog import BaseCog


class MessagingCog(BaseCog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)
        self.subscribe_events()
        
    def subscribe_events(self):
        event_service.subscribe(discord_events.SendDiscordMessage.type, self.handle_send_message_event)
    
    # Handle SendDiscordMessage events and send them to a channel
    async def handle_send_message_event(self, event: discord_events.SendDiscordMessage):
        channel = self.bot.get_channel(event.discord_channel)
        response = await channel.send(event.message)
        return response
    
    # Listen for any messages in channels that the bot is present in.
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Bot handler for messages typed into Discord
        """
        if self.bot.user.id != message.author.id:
            await event_service.post_event(discord_events.ReceiveDiscordMessage(message))

    @app_command()
    async def create_bank(self, interaction: discord.Interaction, bank_name: str):
        event_service.post_event(bank_events.CreateBank(
            discord_channel=interaction.channel_id,
            bank_name=bank_name
        ))

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


def setup(bot):
    bot.load_extension(bot)