from discord.ext.commands import Bot
from discord import Intents 

intents = Intents.default()
intents.message_content = True
intents.members = True

bot = Bot(".",intents=intents)

bot.load_extension("cogs.habitica_cog")




