from app.events.event_service import subscribe
from discord_bot.cogs.bank_cog import BankCog
from habitica.events.habitica_events import AddGoldEventConfirmed

class BankCogeHandlers:
    def __init__(self, bank_cog: BankCog) -> None:
        self.bank_cog = BankCog
        
        subscribe(AddGoldEventConfirmed.type, self.handle_add_user_gold)
    
    async def handle_add_user_gold_confirmed (self, event: AddGoldEventConfirmed):
        await self.bank_cog.add_user_gold(
            event.api_user,
            event.api_token,
            event.amount
        )
    