from dataclasses import dataclass
from discord import Interaction

@dataclass
class SendAccountStatus:
    discord_user_id: str
    discord_channel: str
    interaction: Interaction 
    type = "send_account_status"