from typing import Any
import discord
from discord.ext import commands
from discord.interactions import Interaction

from loguru import logger
import asyncio

from app.bank_service import BankService, BankExistsException, BankNotFoundException, Bank, BankInsufficientFundsException
from app.app_user_service import AppUserService, HabiticaUserLink
from habitica.habitica_service import HabiticaService, InsufficientGoldException, GoldTransactionException
from habitica.events.habitica_events import AddGoldEventConfirmed, AddGoldEvent
from typing import Callable



class UISelectBank(discord.ui.Select):
    def __init__(self, bank_service: BankService):
        self.banks = bank_service.get_banks()
        options = [discord.SelectOption(label=bank.name) for bank in self.banks]
        super().__init__(placeholder="Select Bank", options=options)
    
    async def callback(self, interaction: Interaction) -> Any:
        await interaction.response.defer()


class UISelectHabiticaUser(discord.ui.Select):
    def __init__(self, app_user_service: AppUserService, app_user_id):
        self.habitica_user_links = app_user_service.get_habitica_user_links(app_user_id=app_user_id)
        options = [discord.SelectOption(label=link.name) for link in self.habitica_user_links]
        super().__init__(placeholder="Select Habitica Account", options=options)
    
    async def callback(self, interaction: Interaction) -> Any:
        # Somewhat woried about users trying to register users with the same name in Habitica. But I don't think that's a thing... 
        self.habitica_user = [u for u in self.habitica_user_links if u.name == self.values[0]][0] # Assume first match
        await interaction.response.defer()
    

class UISelectBankAccount(discord.ui.Select):
    def __init__(self, bank_service: BankService, app_user_id):
        self.bank_service = bank_service
        bank_accounts = self.bank_service.get_accounts(app_user_id=app_user_id)

        # Label should contain the bank name, account name, and balance
        options = [discord.SelectOption(label=f"{self.bank_service.get_bank(bank_id=bank_account.bank_id).name}: {bank_account.name}: {bank_account.balance} GP") for bank_account in bank_accounts]
        super().__init__(placeholder="Select Bank: Account", options=options)
    
    async def callback(self, interaction: Interaction) -> Any:
        # Parse out selected option and get the bank account using the bank name and account name, then save it
        bank_name = self.values[0].split(":")[0].strip()
        bank_account_name = self.values[0].split(":")[1].strip()
        bank = self.bank_service.get_bank(bank_name=bank_name)
        self.bank_account = self.bank_service.get_account(bank_id=bank.id, bank_account_name=bank_account_name)
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
        self.app_commands = []
        self.bank_service = bank_service
        self.app_user_service = app_user_service
        self.habitica_service = habitica_service
        logger.info("Habitica Bank Cog initialized.")
    
    @commands.hybrid_group("bank")
    async def bank_commands(self, ctx: commands.Context[commands.Bot]):
        pass
    
    @bank_commands.command(name="create_bank")
    async def create_bank(self, ctx: commands.Context[commands.Bot], bank_name):
        """Create a new bank"""
        logger.info(f"Create Bank was invoked by user {ctx.interaction.user.name}")
        app_user_id = str(ctx.interaction.user.id)

        view = UIView()
        view.add_item(UISelectHabiticaUser(self.app_user_service, app_user_id))
        view.add_item(UIButtonFinish("Create Bank", self.callback_create_bank, original_interaction=ctx.interaction, bank_name=bank_name))
        await ctx.send("Please complete form to open a new Bank account.",view=view, ephemeral=True)

    @bank_commands.command(name="open_bank_account")
    async def open_bank_account(self, ctx: commands.Context[commands.Bot], account_name:str):
        """Open a bank account"""
        logger.info(f"Open Bank Account was invoked by user {ctx.interaction.user.name}")
        app_user_id = str(ctx.interaction.user.id)

        view = UIView()
        view.add_item(UISelectBank(self.bank_service))
        view.add_item(UISelectHabiticaUser(self.app_user_service, app_user_id))
        view.add_item(UIButtonFinish("Open Account", self.callback_open_account, original_interaction=ctx.interaction, account_name=account_name))
        await ctx.send("Please complete form to open a new Bank account.",view=view, ephemeral=True)

    @bank_commands.command()
    async def withdraw_gold(self, ctx: commands.Context[commands.Bot], amount: int):
        """Withdraw gold from bank account"""
        logger.info(f"Withdraw Gold was invoked by user {ctx.interaction.user.name}")
        app_user_id = str(ctx.interaction.user.id)

        view = UIView()
        view.add_item(UISelectBankAccount(self.bank_service, app_user_id))
        view.add_item(UIButtonFinish("Withdraw Gold", self.callback_withdraw_gold, original_interaction=ctx.interaction, amount=amount))
        await ctx.send("Please complete form to open a new Bank account.",view=view, ephemeral=True)

    
    @bank_commands.command()
    async def deposit_gold(self, ctx: commands.Context[commands.Bot], amount: int):
        """Withdraw gold from bank account"""
        logger.info(f"Deposit Gold was invoked by user {ctx.interaction.user.name}")
        app_user_id = str(ctx.interaction.user.id)

        view = UIView()
        view.add_item(UISelectBankAccount(self.bank_service, app_user_id))
        view.add_item(UIButtonFinish("Deposit Gold", self.callback_deposit_gold, original_interaction=ctx.interaction, amount=amount))
        await ctx.send("Please complete form to open a new Bank account.",view=view, ephemeral=True)
        
    async def callback_create_bank(self, interaction: discord.Interaction, finish_button: UIButtonFinish, original_interaction: discord.Interaction, bank_name: str):
        view: discord.ui.View = finish_button.view
        app_user_id = str(interaction.user.id)

        # Get selection values
        for child in view.children:
            if isinstance(child, UISelectHabiticaUser):
                habitica_user_name = child.values[0]
        
        # Defer interaction if no selection data
        if not (bank_name or habitica_user_name or bank_name):
            await interaction.response.defer()
        else:
            # Remove message with view
            await original_interaction.delete_original_response()
            try:
                self.bank_service.create_bank(bank_name=bank_name, owner_id=app_user_id)
                await interaction.response.send_message(f"Created bank '{bank_name}' with owner '{habitica_user_name}'.")
            except Exception as e:
                await interaction.response.send_message(f"Failed to create '{bank_name}' with owner {habitica_user_name}. Error: {e}")
    
    async def callback_open_account(self, interaction: discord.Interaction, finish_button: UIButtonFinish, original_interaction: discord.Interaction, account_name: str):
        view: discord.ui.View = finish_button.view
        bank_name = ""
        habitica_user_name = ""

        # Get selection values
        for child in view.children:
            if isinstance(child, UISelectBank):
                bank_name = child.values[0]
                bank_id = self.bank_service.get_bank(bank_name=bank_name).id
            if isinstance(child, UISelectHabiticaUser):
                habitica_user: HabiticaUserLink = child.values[0]
        
        # Defer interaction if no selection data
        if not (bank_name or habitica_user_name or account_name):
            await interaction.response.defer()
        else:
            # Remove message with view
            await original_interaction.delete_original_response()
            try:
                self.bank_service.open_account(account_name=account_name, bank_id=bank_id, habitica_user_id=habitica_user.api_user)
                await interaction.response.send_message(f"Created bank account {account_name} in bank {bank_name}.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Failed to open bank account '{account_name}' in bank '{bank_name}'. Error: {e}")
                raise e

    async def callback_withdraw_gold(self, interaction: discord.Interaction, finish_button: UIButtonFinish, original_interaction: discord.Interaction, amount: int):
        view: discord.ui.View = finish_button.view
        gold_add_successful = False
        gold_withdraw_successful = False

        # Get selection values
        for child in view.children:
            if isinstance(child, UISelectBankAccount):
                bank_account = child.bank_account
                habitica_user = self.app_user_service.get_habitica_user_link(habitica_user_id=bank_account.habitica_user_id)

        # Defer interaction if no selection data
        if not (bank_account or amount):
            await interaction.response.defer()
        else:
            # Remove message with view
            await original_interaction.delete_original_response()
            try:
                # Must withdraw from bank first to see if exception like insufficient funds is thrown
                self.bank_service.withdraw(amount=amount, bank_account_id=bank_account.id, habitica_user_id=habitica_user.api_user, bank_id=bank_account.bank_id)
                gold_withdraw_successful = True
                await self.habitica_service.add_user_gold(api_user=habitica_user.api_user, api_token=habitica_user.api_token, amount=amount)
                gold_add_successful = True # Verify we didn't raise exception on add_user_gold
                await interaction.response.send_message(f"Withdrew {amount} from account {bank_account.name}. New balance is {bank_account.balance}", ephemeral=True)
            except Exception as e:
                # If the update gold to habitica account failed and money was withdrawn, deposit the money back into bank account
                if not gold_add_successful and gold_withdraw_successful:
                    self.bank_service.deposit(amount=amount, bank_account_id=bank_account.id, habitica_user_id=habitica_user.api_user, bank_id=bank_account.bank_id)
                await interaction.response.send_message(f"Failed to withdraw '{amount}' from bank account '{bank_account.name}'. Error: {e}", ephemeral=True)
                raise e

    async def callback_deposit_gold(self, interaction: discord.Interaction, finish_button: UIButtonFinish, original_interaction: discord.Interaction, amount: int):
        view: discord.ui.View = finish_button.view
        gold_remove_successful = False
        gold_deposit_successful = False

        # Get selection values
        for child in view.children:
            if isinstance(child, UISelectBankAccount):
                bank_account = child.bank_account
                habitica_user = self.app_user_service.get_habitica_user_link(habitica_user_id=bank_account.habitica_user_id)

        # Defer interaction if no selection data
        if not (bank_account or amount):
            await interaction.response.defer()
        else:
            # Remove message with view
            await original_interaction.delete_original_response()
            try:
                # Must remove gold from user first to see if exception like insufficient gold is thrown
                await self.habitica_service.add_user_gold(api_user=habitica_user.api_user, api_token=habitica_user.api_token, amount=-amount)
                gold_remove_successful = True
                self.bank_service.deposit(amount=amount, habitica_user_id=habitica_user.api_user, bank_account_id=bank_account.id, bank_id=bank_account.bank_id)
                gold_deposit_successful = True # Verify we didn't raise exception on add_user_gold
                await interaction.response.send_message(f"Deposited {amount} into account {bank_account.name}. New balance is {bank_account.balance}", ephemeral=True)
            except Exception as e:
                # If the deposit to bank fails and gold was removed from user, give the money back to the user
                if not gold_deposit_successful and gold_remove_successful:
                    await self.habitica_service.add_user_gold(api_user=habitica_user.api_user, api_token=habitica_user.api_token, amount=amount)
                await interaction.response.send_message(f"Failed to deposit '{amount}' into bank account '{bank_account.name}'. Error: {e}", ephemeral=True)
                raise e