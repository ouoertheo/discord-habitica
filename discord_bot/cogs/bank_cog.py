from typing import Any
import discord
from discord.ext import commands
from discord.interactions import Interaction

from loguru import logger
import asyncio

from app.bank_service import BankService, BankAccount, BankLoanAccount, Bank
from app.app_user_service import AppUserService, HabiticaUserLink
from habitica.habitica_service import HabiticaService, InsufficientGoldException, GoldTransactionException

from app.events.event_service import post_event
from app.events.bank_events import WithdrawGold, DepositGold

from typing import Callable



class UISelectBank(discord.ui.Select):
    def __init__(self, banks):
        options = [discord.SelectOption(label=bank.name) for bank in banks]
        super().__init__(placeholder="Select Bank", options=options)
    
    async def callback(self, interaction: Interaction) -> Any:
        await interaction.response.defer()


class UISelectHabiticaUser(discord.ui.Select):
    def __init__(self, habitica_user_links):
        self.habitica_user_links = habitica_user_links
        options = [discord.SelectOption(label=link.name) for link in habitica_user_links]
        super().__init__(placeholder="Select Habitica Account", options=options)
    
    async def callback(self, interaction: Interaction) -> Any:
        await interaction.response.defer()
    

class UISelectBankAccount(discord.ui.Select):
    def __init__(self, bank_accounts: list[BankAccount|BankLoanAccount]):
        self.bank_accounts = bank_accounts

        # Label should contain the bank name, account name, and balance
        options = [discord.SelectOption(label=bank_account) for bank_account in bank_accounts]
        super().__init__(placeholder="Select Bank: Account", options=options)
    
    async def callback(self, interaction: Interaction) -> Any:
        await interaction.response.defer()


class UIButtonFinish(discord.ui.Button):
    def __init__(self, label:str, callback: Callable, original_interaction: discord.Interaction, **kwargs):
        super().__init__(label=label)
        self.kwargs = kwargs
        self.original_interaction = original_interaction
        self.parent_callback = callback
        
    async def callback(self, interaction: Interaction) -> Any:
        await self.parent_callback(interaction, self, original_interaction=self.original_interaction, **self.kwargs)


class UIView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)


class BankCog(commands.Cog):
    def __init__(
            self, 
            bot: commands.bot, 
            bank_service: BankService, 
            app_user_service: AppUserService,
            habitica_service: HabiticaService
        ) -> None:
        self.bot = bot
        self.app_commands = []
        self.bank_service = bank_service
        self.app_user_service = app_user_service
        self.habitica_service = habitica_service
        logger.info("Habitica Bank Cog initialized.")
    
    #################################
    ### Verification of Existence ###
    #################################
        
    async def get_banks(self, ctx: commands.Context[commands.Bot]):
        banks =  self.bank_service.get_banks()
        if not banks:
            message = "⚠️ There are no existing banks. A bank must exist before you can do that."
            await ctx.send(message, ephemeral=True)
            raise Exception(message)
        return banks

    async def get_habitica_user_links(self, ctx: commands.Context[commands.Bot], discord_user_id):
        # Check Habitica account is registered
        habitica_user_links = self.app_user_service.get_habitica_user_links(app_user_id=discord_user_id)
        if not habitica_user_links:
            message = "⚠️ You must register a Habitica account before you can do that."
            await ctx.send(message, ephemeral=True)
            raise Exception(message)
        return habitica_user_links

    async def get_bank_accounts(self, ctx: commands.Context[commands.Bot], discord_user_id):
        self.get_habitica_user_links(ctx, discord_user_id)
        bank_accounts = self.bank_service.get_accounts(app_user_id=discord_user_id)
        if not bank_accounts:
            message = "⚠️ You must open a bank account before you can do that."
            await ctx.send(message, ephemeral=True)
            raise Exception(message)
        return bank_accounts

    ######################
    ###### Commands ######
    ######################

    @commands.hybrid_group("bank")
    async def bank_commands(self, ctx: commands.Context[commands.Bot]):
        pass
    
    @bank_commands.command(name="create_bank")
    async def create_bank(self, ctx: commands.Context[commands.Bot], bank_name):
        """Create a new bank"""
        logger.info(f"Create Bank was invoked by user {ctx.interaction.user.name}")
        discord_user_id = str(ctx.interaction.user.id)
        
        try:
            self.bank_service.create_bank(bank_name=bank_name, app_user_id=discord_user_id)
            await ctx.interaction.response.send_message(f"🏦 Created bank '{bank_name}' with owner '{ctx.interaction.user.name}'.")
        except Exception as e:
            await ctx.interaction.response.send_message(f"⛔ Failed to create '{bank_name}' with owner {ctx.interaction.user.name}. Error: {e}")

    @bank_commands.command(name="open_bank_account")
    async def open_bank_account(self, ctx: commands.Context[commands.Bot], account_name:str):
        """Open a bank account"""
        logger.info(f"Open Bank Account was invoked by user {ctx.interaction.user.name}")

        banks = await self.get_banks(ctx)
        habitica_user_links = await self.get_habitica_user_links(ctx, ctx.interaction.user.id)
            
        view = UIView()
        view.add_item(UISelectBank(banks))
        view.add_item(UISelectHabiticaUser(habitica_user_links))
        view.add_item(UIButtonFinish("Open Account", self.callback_open_account, original_interaction=ctx.interaction, account_name=account_name))
        await ctx.send("Please complete form to open a new Bank account.",view=view, ephemeral=True)

    @bank_commands.command()
    async def withdraw_gold(self, ctx: commands.Context[commands.Bot], amount: int):
        """Withdraw gold from bank account"""
        logger.info(f"Withdraw Gold was invoked by user {ctx.interaction.user.name}")
        discord_user_id = str(ctx.interaction.user.id)

        bank_accounts = await self.get_bank_accounts(ctx, discord_user_id)

        # This is how options will be rendered
        options = [f"{self.bank_service.get_bank(bank_id=bank_account.bank_id).name}: {bank_account.name}: {bank_account.balance} GP" for bank_account in bank_accounts]

        view = UIView()
        view.add_item(UISelectBankAccount(options))
        view.add_item(UIButtonFinish("Withdraw Gold", self.callback_withdraw_gold, original_interaction=ctx.interaction, amount=amount))
        await ctx.send("Select bank account to withdraw gold from.",view=view, ephemeral=True)

    
    @bank_commands.command()
    async def deposit_gold(self, ctx: commands.Context[commands.Bot], amount: int):
        """Withdraw gold from bank account"""
        logger.info(f"Deposit Gold was invoked by user {ctx.interaction.user.name}")
        discord_user_id = str(ctx.interaction.user.id)

        bank_accounts = await self.get_bank_accounts(ctx, discord_user_id)

        # This is how options will be rendered
        options = [f"{self.bank_service.get_bank(bank_id=bank_account.bank_id).name}: {bank_account.name}: {bank_account.balance} GP" for bank_account in bank_accounts]

        view = UIView()
        view.add_item(UISelectBankAccount(options))
        view.add_item(UIButtonFinish("Deposit Gold", self.callback_deposit_gold, original_interaction=ctx.interaction, amount=amount))
        await ctx.send("Select a bank account to deposit gold into.",view=view, ephemeral=True)

    #####################
    ### Callback Code ###
    #####################
    
    async def callback_open_account(self, interaction: discord.Interaction, finish_button: UIButtonFinish, original_interaction: discord.Interaction, account_name: str):
        view: discord.ui.View = finish_button.view
        discord_user_id = str(interaction.user.id)

        # Get selection values
        for component in view.children:
            if isinstance(component, UISelectBank):
                selection = component.values[0]
                bank = self.bank_service.get_bank(bank_name=selection)
            if isinstance(component, UISelectHabiticaUser):
                selection = component.values[0]
                habitica_user_link = self.app_user_service.get_habitica_user_link(app_user_id=str(interaction.user.id),habitica_user_name=selection)
        
        # Defer interaction if no selection data
        if not (bank or habitica_user_link or account_name):
            await interaction.response.defer()
        else:
            # Remove message with view
            await original_interaction.delete_original_response()
            try:
                self.bank_service.open_account(account_name=account_name, bank_id=bank.id, app_user_id=discord_user_id, habitica_user_id=habitica_user_link.api_user)
                await interaction.response.send_message(f"✅ Created bank account {account_name} in bank {bank.name}.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"⛔ Failed to open bank account '{account_name}' in bank '{bank.name}'. Error: {e}",ephemeral=True)
                raise e

    async def callback_withdraw_gold(self, interaction: discord.Interaction, finish_button: UIButtonFinish, original_interaction: discord.Interaction, amount: int):
        view: discord.ui.View = finish_button.view

        # Get selection values
        for component in view.children:
            if isinstance(component, UISelectBankAccount):
                # Parse out selected option and get the bank account using the bank name and account name
                bank_name = component.values[0].split(":")[0].strip()
                bank = self.bank_service.get_bank(bank_name=bank_name)
                bank_account_name = component.values[0].split(":")[1].strip()

                bank_account = self.bank_service.get_account(bank_id=bank.id, bank_account_name=bank_account_name)

        # Defer interaction if no selection data
        if bank_account or amount:
            event = WithdrawGold(amount=amount, bank_id=bank_account.bank_id, bank_account_id=bank_account.id, description="", interaction=interaction)
            asyncio.create_task(post_event(event))
        else:
            # Remove message with view
            await original_interaction.delete_original_response()
            

    async def callback_deposit_gold(self, interaction: discord.Interaction, finish_button: UIButtonFinish, original_interaction: discord.Interaction, amount: int):
        view: discord.ui.View = finish_button.view
        amount = -amount
        # Get selection values
        for component in view.children:
            if isinstance(component, UISelectBankAccount):
                # Parse out selected option and get the bank account using the bank name and account name
                bank_name = component.values[0].split(":")[0].strip()
                bank = self.bank_service.get_bank(bank_name=bank_name)
                bank_account_name = component.values[0].split(":")[1].strip()

                bank_account = self.bank_service.get_account(bank_id=bank.id, bank_account_name=bank_account_name)

        # Defer interaction if no selection data
        if bank_account and amount:
            event = WithdrawGold(amount=amount, bank_id=bank_account.bank_id, bank_account_id=bank_account.id, description="", interaction=interaction)
            asyncio.create_task(post_event(event))
        else:
            # Remove message with view
            await original_interaction.delete_original_response()