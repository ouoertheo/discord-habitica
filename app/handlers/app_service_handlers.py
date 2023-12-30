from app.events.app_events import SendAccountStatus
from app.events.discord_events import SendDiscordMessage
from app.events.event_service import subscribe, post_event
from app.app_service import AppService

class AppServiceHandlers:
    def __init__(self, app_service: AppService) -> None:
        self.app_service = app_service
        subscribe(SendAccountStatus.type, self.send_account_status)

    async def send_account_status(self, event: SendAccountStatus):
        message = await self.app_service.get_status_message(event.discord_user_id)
        await post_event(SendDiscordMessage(interaction=event.interaction, message=message, ephemeral=True))
