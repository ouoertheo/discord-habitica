from app.events import event_service, habitica_events
from habitica import habitica_api
from habitica.model import HabiticaUser
import os, dotenv
dotenv.load_dotenv()
SERVER_URL = os.getenv("SERVER_URL")

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
        "Calls Habitica for user and returns a HabiticaUser object."
        user_json  = await self.habitica_api.get_user(api_user, api_token)
        user = HabiticaUser.load(user_json)
        return user
    
    async def add_user_gold(self, event: habitica_events.AddHabiticaGold):
        "Add or remove user gold. Set amount to negative to remove gold."
        user = await self.get_user(event.api_user, event.api_token)
        current_gold = user.stats.gp
        new_gold = current_gold + event.amount
        payload = {
            "stats.gp": new_gold
        }
        await self.habitica_api.update_user(event.api_user, event.api_token, payload)

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
