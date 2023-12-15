import app.events.bank_events as bank_events
from  app.bank_service import BankService
from app.app_user_service import AppUserService, UserMapNotFoundException
from habitica.habitica_service import HabiticaService
from app.events.event_service import post_event, subscribe
from app.events.discord_events import SendDiscordMessage


class BankEventHandlers:
    def __init__(self, bank_service: BankService, app_user_service: AppUserService, habitica_service: HabiticaService) -> None:
        self.bank_service = bank_service
        self.app_user_service = app_user_service
        self.habitica_service = habitica_service
        subscribe(bank_events.CreateBank.type, self.handle_create_bank_event)

    async def handle_create_bank_event(self, event: bank_events.CreateBank):
        try:
            # Make sure the user exists in order to assign as owner
            user_link = self.app_user_service.get_habitica_user_link(habitica_user_id=event.habitica_api_user)
            self.bank_service.create_bank(event.bank_name, user_link.api_user)
            post_event(SendDiscordMessage(event.discord_channel_id, f"Bank {event.bank_name} created."))
        except UserMapNotFoundException as e:
            post_event(SendDiscordMessage(event.discord_channel_id, f"Failed to create bank. Error: {e}"))
    
    async def handle_bank_withdraw(self, event: bank_events.WithdrawGold):
        try:
            # Get objects given event details
            bank_account = self.bank_service.get_account(event.bank_id, bank_account_id=event.bank_account_id)
            habitica_user = self.app_user_service.get_habitica_user_link(habitica_user_id=bank_account.habitica_user_id)

            # Create transaction and initiate withdrawal.
            transaction = self.bank_service.create_transaction(bank_account.bank_id, bank_account.id, event.amount, event.description)
            self.bank_service.withdraw(transaction)
            
            await self.habitica_service.add_user_gold(api_user=habitica_user.api_user, api_token=habitica_user.api_token, amount=event.amount)
            await post_event(SendDiscordMessage(f"Withdrew {event.amount} from account {bank_account.name}. New balance is {bank_account.balance}", ephemeral=True))
        except Exception as e:
            # If the update gold to habitica account failed and money was withdrawn, deposit the money back into bank account
            if transaction.src_completed and not transaction.dst_completed:
                rollback_transaction = self.bank_service.create_transaction(bank_account.bank_id, bank_account.id, event.amount, event.description)
                self.bank_service.deposit(amount=transaction.amount, bank_account_id=bank_account.id, habitica_user_id=habitica_user.api_user, bank_id=bank_account.bank_id)
            await post_event(SendDiscordMessage(f"Failed to withdraw '{amount}' from bank account '{bank_account.name}'. Error: {e}", ephemeral=True))
            raise e