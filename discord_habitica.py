
from discord.ext.commands import Bot
from discord import Intents 
from discord_bot.bot import DiscordHabiticaBot

import asyncio
from loguru import logger
import logging
import inspect
import sys
from uvicorn import Config, Server
from enum import Enum
from dataclasses import dataclass

# App Imports
import config as cfg
from app.webhook_service import webhook_fastapi_app
from persistence.file_driver_new import PersistenceFileDriver
import habitica.habitica_api as api

# Service Imports
from habitica.habitica_service import HabiticaService
from app.app_service import AppService
from app.bank_service import BankService
from app.app_user_service import AppUserService

# Handler Imports
from habitica.handlers.habitica_service_handlers import HabiticaServiceHandlers

# Set logging levels. Intercept all logs
logger.remove()
logger.add(sink=sys.stdout, level="INFO")
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Handle async errors? Do I really need this?
async def handle_exception(loop, context):
    msg = context.get("exception", context["message"])
    logger.error(f"Caught exception: {msg}")

# Handler dependency injection class.
@dataclass
class EventHandlers:
    habitica_service_handlers: HabiticaServiceHandlers


async def main():
    invite_url = "https://discord.com/oauth2/authorize?client_id=1012353261916913704&permissions=17979471359040&scope=bot"
    logger.info(f"Starting Discord Habitica. Invite URL: {invite_url}")

    driver = PersistenceFileDriver("store")

    # TODO: Create a dependency injection class for Service Dependencies.
    # Service Dependencies 
    app_user_service = AppUserService(driver)
    bank_service = BankService(driver)
    habitica_service = HabiticaService(api)
    app_service = AppService(
        api,
        driver,
        app_user_service,
        bank_service,
        habitica_service
    )

    # Event Handlers
    event_handlers = EventHandlers(
        habitica_service_handlers=HabiticaServiceHandlers(habitica_service)
    )

    # Create bot
    bot = DiscordHabiticaBot(prefix="!", ext_dir="discord_bot/cogs", app_service=app_service)


    # Initialize asyncio loop
    loop = asyncio.new_event_loop()
    loop.set_exception_handler(handle_exception)
    
    # Configure Webhook Server
    webhook_fastapi_app_config = Config(webhook_fastapi_app, host="0.0.0.0", port=12555, loop=loop)
    webhook_fastapi_app_server = Server(webhook_fastapi_app_config)

    await asyncio.gather(
        bot.start(cfg.DISCORD_TOKEN),
        webhook_fastapi_app_server.serve()
    )

if __name__ == "__main__":
    asyncio.run(main())