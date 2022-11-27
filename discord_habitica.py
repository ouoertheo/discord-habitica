
from discord.ext.commands import Bot
from discord import Intents 
import asyncio
import config as cfg
from cogs.habitica_cog import HabiticaCog

logger = cfg.logging.getLogger(__name__)

intents = Intents.default()
intents.message_content = True
intents.members = True
bot = Bot(".",intents=intents)

async def handle_exception(loop, context):
    msg = context.get("exception", context["message"])
    logger.error(f"Caught exception: {msg}")

async def main():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    await asyncio.gather(
        bot.add_cog(HabiticaCog(bot)),
        bot.start(cfg.DISCORD_TOKEN),
    )

if __name__ == "__main__":
    asyncio.run(main())