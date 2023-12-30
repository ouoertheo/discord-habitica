from app.events import event_service, habitica_events
from habitica import habitica_api
from habitica.model import HabiticaUser
from habitica.events.habitica_events import AddGoldEventConfirmed
from loguru import logger
import os, dotenv
import asyncio
dotenv.load_dotenv()
SERVER_URL = os.getenv("SERVER_URL")
from app.transaction_service import ledger, Operation, RollbackException

class InsufficientGoldException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        logger.error(args[0])

class GoldTransactionException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        logger.error(args[0])
class HabiticaService:
    """
    Single interface for interacting with objects
    """
    def __init__(self, habitica_api = habitica_api) -> None:
        self.habitica_api = habitica_api
        self.subscribe_events()

    # TODO: move these events out to the app. No point being here.
    def subscribe_events(self):
        event_service.subscribe(habitica_events.CreateAllWebhookSubscription.type, self.handle_create_all_webhooks_event)
        event_service.subscribe(habitica_events.DeleteAllWebhookSubscription.type, self.handle_delete_all_webhooks_event)
        event_service.subscribe(habitica_events.WebhookSubscriptionEvent.type, self.handle_create_webhook_event)
        event_service.subscribe(habitica_events.WebhookSubscriptionDeleteEvent.type, self.handle_delete_webhook_event)
        event_service.subscribe(habitica_events.AddHabiticaGold.type, self.add_user_gold)

    async def get_user(self, api_user, api_token):
        """Calls Habitica for user and returns a HabiticaUser object."""
        user_json  = await self.habitica_api.get_user(api_user, api_token)
        user = HabiticaUser.load(user_json)
        return user
    
    async def add_user_gold(self, api_user, api_token, amount):
        """Add or remove user gold. Set amount to negative to remove gold."""
        logger.info(f"Initiating gold transaction for amount {amount} with Habitica for api_user {api_user}...")
        user = await self.get_user(api_user, api_token)
        current_gold = user.stats.gp

        if current_gold + amount < 0:
            raise InsufficientGoldException(f"Habitica user {user.profile.name} has insufficient GP. Current GP is {current_gold}.")
        
        new_gold = current_gold + amount

        # Record the operation to the ledger
        operation_object = {"api_user": api_user,"api_token": api_token}
        operation = ledger.add_operation(operation_object, 'gp',current_gold, new_gold, self.rollback_gold)

        payload = {"stats.gp": new_gold}
        await self.habitica_api.update_user(api_user, api_token, payload)

        # Verify gold was added.
        user = await self.get_user(api_user, api_token)
        if new_gold != user.stats.gp:
            operation.success = False
            raise GoldTransactionException(f"Something went wrong updating Habitica User: '{user.profile.name}' gold. API_USER: '{api_user}'.")
        
        # Mark operation as successful in ledger
        operation.success = True
        logger.info(f"Added {amount} gold to habitica account for name: {user.profile.name}, api_user: {api_user}")
    
    async def rollback_gold(self, operation: Operation):
        try:
            # Reverse add gold
            self.add_user_gold(
                operation.obj['api_user'],
                operation.obj['api_token'], 
                operation.old_value - operation.new_value
            )
        except Exception as e:
            raise RollbackException(f"Failed to roll back addition of gold. Exception info: {str(e)}")


    async def handle_create_webhook_event(self, event: habitica_events.WebhookSubscriptionEvent):
        payload = {}
        payload['url'] = SERVER_URL
        payload['label'] =  f"Discord Habitica {event.webhook_type} Webhook"
        payload['type'] = event.webhook_type
        payload['options'] = event.options
        await self.habitica_api.create_webhook(event.api_user, event.api_token, payload)
    
    async def handle_create_all_webhooks_event(self, event: habitica_events.CreateAllWebhookSubscription):
        user = await self.get_user(event.api_user, event.api_token)
        webhook_subscriptions: list[habitica_events.WebhookSubscriptionEvent] = [
            habitica_events.TaskWebhookSubscriptionEvent(event.api_user, event.api_token),
            habitica_events.UserWebhookSubscriptionEvent(event.api_user, event.api_token),
            habitica_events.QuestWebhookSubscriptionEvent(event.api_user, event.api_token),
            habitica_events.GroupChatWebhookSubscriptionEvent(event.api_user, event.api_token, user.party._id),
        ]
        for webhook in webhook_subscriptions:
            if not webhook.webhook_type in [w['type'] for w in user.webhooks]:
                await self.handle_create_webhook_event(webhook)
    
    async def handle_delete_webhook_event(self, event: habitica_events.WebhookSubscriptionDeleteEvent):
        await self.habitica_api.delete_webhook(event.api_user, event.api_token, event.id)
    
    async def handle_delete_all_webhooks_event(self, event: habitica_events.DeleteAllWebhookSubscription):
        user = await self.get_user(event.api_user, event.api_token)
        for webhook in user.webhooks:
            if "Discord Habitica" in webhook['label']:
                evt = habitica_events.WebhookSubscriptionDeleteEvent(event.api_user, event.api_token, webhook['id'])
                await event_service.post_event(evt)
