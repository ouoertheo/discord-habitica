from typing import Optional
import discord
from discord.ext import commands
from discord.app_commands import command as app_command, Choice, choices
from discord.interactions import Interaction
from discord.utils import MISSING
from cogs.base_cog import BaseCog

from loguru import logger

from app.bank_service import BankService
from app.app_user_service import AppUserService


class CreateBankModal(discord.ui.Modal):
    def __init__(self, habitica_user_options, bank_service: BankService):
        super().__init__(title="Create Bank")
        self.bank_service = bank_service
        self.add_item(discord.ui.TextInput(label="Bank Name"))
        self.add_item(discord.ui.Select(placeholder="Select Owner", min_values=1, max_values=10, options=habitica_user_options))
        
    
    async def on_submit(self, interaction: Interaction) -> None:
        self.from_message
        self.bank_service.create_bank()

class BankCog(BaseCog):
    def __init__(
            self, 
            bot: commands.bot, 
            bank_service: BankService, 
            app_user_service: AppUserService
        ) -> None:
        super().__init__(bot)
        self.app_commands = []
        self.bank_service = bank_service
        self.app_user_service = app_user_service
    
    @app_command(name="Create Bank")
    async def create_bank(self, interaction: discord.Interaction):
        try:
            discord_user = interaction.user.id
            habitica_users = self.app_user_service.get_habitica_user_links(app_user_id=str(discord_user))
            habitica_user_options = [discord.SelectOption(label=user.name) for user in habitica_users]
            await interaction.response.send_modal(CreateBankModal(habitica_user_options, self.bank_service))
        except Exception as e:
            await interaction.response.send_message(f"Failed to created bank: {e}")
            
def setup(bot):
    bot.load_extension(bot)