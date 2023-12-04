
class AddHabiticaGold:
    type = "add_habitica_gold"
    def __init__(self, api_user, api_token, amount) -> None:
        self.api_user = api_user
        self.api_token = api_token
        self.amount = amount


####################################
## Habitica Webhook Subscriptions ##
####################################
class QuestWebhookSubscriptionEvent:
    type = "webhook_subscription_event"
    def __init__(self, api_user, api_token, questStarted: bool = True, questFinished: bool = True, questInvited: bool = True) -> None:
        self.api_user = api_user
        self.api_token = api_token
        self.options = {
            "questStarted": questStarted,
            "questFinished": questFinished,
            "questInvited": questInvited,
        }
        self.webhook_type = "questActivity"
    
class UserWebhookSubscriptionEvent:
    type = "webhook_subscription_event"
    def __init__(self,
                api_user,
                api_token,
                petHatched: bool = False,
                mountRaised: bool = False,
                leveledUp: bool = True,
            ) -> None:
        self.api_user = api_user
        self.api_token = api_token
        self.options = {
            "petHatched": petHatched,
            "mountRaised": mountRaised,
            "leveledUp": leveledUp,
        }
        self.webhook_type = "userActivity"

class GroupChatWebhookSubscriptionEvent:
    type = "webhook_subscription_event"
    def __init__(self, api_user, api_token, groupId: str) -> None:
        self.api_user = api_user
        self.api_token = api_token
        self.options = {"groupId": groupId}
        self.webhook_type = "groupChatReceived"

class TaskWebhookSubscriptionEvent:
    type = "webhook_subscription_event"
    def __init__(self,
                api_user,
                api_token,
                created: bool = False,
                updated: bool = False,
                deleted: bool = False,
                checklistScored: bool = False,
                scored: bool = True
            ) -> None:
        self.api_user = api_user
        self.api_token = api_token
        self.options = {
            "created": created,
            "updated": updated,
            "deleted": deleted,
            "checklistScored": checklistScored,
            "scored": scored,
        }
        self.webhook_type = "taskActivity"
        
class WebhookSubscriptionDeleteEvent:
    type = "webhook_subscription_delete_event"
    def __init__(self, api_user, api_token, id) -> None:
        self.api_user = api_user
        self.api_token = api_token
        self.id = id

class WebhookSubscriptionEvent:
    type = "webhook_subscription_event"
    "Base event class for creating webhooks."
    def __init__(self, api_user, api_token, type, options) -> None:
        self.options = options
        self.api_user = api_user
        self.api_token = api_token
        self.webhook_type = "none"
        
class CreateAllWebhookSubscription:
    type = "create_all_webhook_subscriptions_event"
    def __init__(self, api_user, api_token) -> None:
        self.api_user = api_user
        self.api_token = api_token

class DeleteAllWebhookSubscription:
    type = "delete_all_webhook_subscriptions_event"
    def __init__(self, api_user, api_token) -> None:
        self.api_user = api_user
        self.api_token = api_token