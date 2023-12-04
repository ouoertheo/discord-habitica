import app.events.bank_events as bank_events
from  app.bank_service import BankService
from app.app_user_service import AppUserService, UserMapNotFoundException
from app.events.event_service import post_event, subscribe
from app.events.discord_events import SendDiscordMessage


class BankEventHandlers:
    def __init__(self, bank_service: BankService, app_user_service: AppUserService) -> None:
        self.bank_service = bank_service
        self.app_user_service = app_user_service
        subscribe(bank_events.CreateBank.type, self.handle_create_bank_event)

    async def handle_create_bank_event(self, event: bank_events.CreateBank):
        try:
            # Make sure the user exists in order to assign as owner
            user_link = self.app_user_service.get_habitica_user_link(api_user=event.habitica_api_user)
            self.bank_service.create_bank(event.bank_name, user_link.api_user)
            post_event(SendDiscordMessage(event.discord_channel_id, f"Bank {event.bank_name} created."))
        except UserMapNotFoundException as e:
            post_event(SendDiscordMessage(event.discord_channel_id, f"Failed to create bank. Error: {e}"))
