from discord.ext import commands


class HabiticaCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    async def send_message(self, channel_id, content):
        channel = self.bot.fetch_channel(channel_id)
        await channel.send(content)
    
    async def receive_message(self, ctx: commands.Context):
        """
        How am I going to feed the messages/commamnds
        back to Habitica?
        """

    
    
    

def setup(bot):
    bot.load_extension(bot)