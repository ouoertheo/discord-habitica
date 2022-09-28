import logging
import dotenv, os

logger = logging.getLogger(__name__)

dotenv.load_dotenv(".env")
ENVIRONMENT = os.getenv("ENVIRONMENT")

if ENVIRONMENT == "PROD":
    logger.info("Using prod configs")
    EXTERNAL_SERVER_URL = os.getenv("EXTERNAL_SERVER_URL")
    EXTERNAL_SERVER_PORT = os.getenv("EXTERNAL_SERVER_PORT")
elif ENVIRONMENT == "DEV":
    logger.info("Using dev configs")
    EXTERNAL_SERVER_URL = os.getenv("DEV_EXTERNAL_SERVER_URL")
    EXTERNAL_SERVER_PORT = os.getenv("DEV_EXTERNAL_SERVER_PORT")

LOCAL_SERVER_URL = f"{EXTERNAL_SERVER_URL}:{EXTERNAL_SERVER_PORT}/habitica"

class WebHook:
    QUEST = "questActivity"
    USER = "userActivity"
    GROUP_CHAT = "groupChatReceived"
    TASK = "taskActivity"
    _payload = {}

    TASK_OPTIONS = {
        "created": False,
        "updated": False,
        "deleted": False,
        "checklistScored": False,
        "scored": True
    }

    GROUP_CHAT_OPTIONS = {
        "groupId": "required-uuid-of-group"
    }
    "groupId required"

    USER_OPTIONS = {
        "petHatched": False,
        "mountRaised": False,
        "leveledUp": True,
    }
    "set at least one to true"

    QUEST_OPTIONS = {
        "questStarted": True,
        "questFinished": True,
        "questInvited": True,
    }
    "set at least one to true"

    def __init__(self, webhook_type, user_id, options={}, webhook_id="") -> None:
        if webhook_type not in [self.QUEST, self.USER, self.GROUP_CHAT, self.TASK]:
            raise ValueError(f"Invalid webhook_type provided: {webhook_type}")
        self.webhook_type = webhook_type
        self.custom_options = options
        self.id = webhook_id
        self.user_id = user_id

    @property
    def payload(self):
        self._payload = {
            "enabled": True,
            "url": LOCAL_SERVER_URL
        }

        if self.webhook_type == self.QUEST:
            self._payload['label'] = "Discord Habitica Quest Webhook"
            self._payload['type'] = self.QUEST
            self._payload['options'] = self.custom_options or self.QUEST_OPTIONS

        if self.webhook_type == self.USER:
            self._payload['label'] = "Discord Habitica User Webhook"
            self._payload['type'] = self.USER
            self._payload['options'] = self.custom_options or self.USER_OPTIONS

        if self.webhook_type == self.GROUP_CHAT:
            self._payload['label'] = "Discord Habitica Group Chat Webhook"
            self._payload['type'] = self.GROUP_CHAT
            self._payload['options'] = self.custom_options or self.GROUP_CHAT_OPTIONS

        if self.webhook_type == self.TASK:
            self._payload['label'] = "Discord Habitica Task Webhook"
            self._payload['type'] = self.TASK
            self._payload['options'] = self.custom_options or self.TASK_OPTIONS
        
        return self._payload

def load_webhooks():
    pass