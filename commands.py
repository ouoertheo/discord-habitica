from discord.ext.commands import Bot
import discord 
from discord.app_commands import command

import discord
from config import logging

logger = logging.getLogger(__name__)


@command()
async def test_command(interaction: discord.Interaction, arg1:str, arg2:str):
    print(f"{arg1} {arg2}")
    await interaction.response.send_message("Ok!")

command_list = [
    test_command
]

async def register_commands(discord_bot: Bot):
    for command in command_list:
        discord_bot.tree.add_command(command)
    await discord_bot.tree.sync()
