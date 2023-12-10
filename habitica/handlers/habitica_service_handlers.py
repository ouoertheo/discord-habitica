from app.events.event_service import subscribe
from habitica.habitica_service import HabiticaService
from habitica.events.habitica_events import AddGoldEvent

class HabiticaServiceHandlers:
    def __init__(self, habitica_service: HabiticaService) -> None:
        self.habitica_service = habitica_service
        
        subscribe(AddGoldEvent.type, self.handle_add_user_gold)
    
    async def handle_add_user_gold(self, event: AddGoldEvent):
        await self.habitica_service.add_user_gold(
            event.api_user,
            event.api_token,
            event.amount
        )
    