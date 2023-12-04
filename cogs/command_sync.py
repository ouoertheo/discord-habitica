import discord
from discord.ext import commands
from discord.app_commands import command as app_command
from loguru import logger

command_list = []

async def clear_commands(bot: commands.Bot):
    bot.tree.clear_commands(guild=None)
    logger.info("Syncing commands. This could take a while...")
    bot.tree.sync()
    logger.info(f"Cleared remote command tree")

async def sync_commands(bot: commands.Bot):
    new_commands = []

    # Add commands that are not in the command tree
    for command in command_list:
        if not bot.tree.get_command(command.name):
            try:
                bot.tree.add_command(command)
                new_commands.append(command.name)
                logger.info(f"Registered command: {command.name}")
            except Exception as e:
                logger.error(e)
    
    # Sync only if there are new commands
    if new_commands:
        logger.info("Syncing commands. This could take a while...")
        await bot.tree.sync()
        logger.info(f"Synced local command tree")
    else:
        logger.info("No new commands to sync. Skipping sync.")