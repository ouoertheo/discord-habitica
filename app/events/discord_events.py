from dataclasses import dataclass
from discord import Interaction

@dataclass
class SendDiscordMessage:
    """ 
    Send message to Discord. discord_channel, discord_user_id, and interaction are mutually exclusive. 
    If more than one specified, message will only be sent to one in the order of precedence listed below.

    `discord_channel`: if specified will send to discord channel
    `discord_user_id`: if specified will DM user
    `interaction`: if specified will attempt to respond to interaction
    `ephemeral`: if specified, will respond to interaction visible only to user
    """
    message: str
    discord_channel: str = ""
    discord_user_id: str = ""
    interaction: Interaction = None
    ephemeral: bool = False
    type = "send_discord_message"
    
class ReceiveDiscordMessage:
    type = "receive_discord_message"
    def __init__(self, discord_message) -> None:
        self.discord_message = discord_message
