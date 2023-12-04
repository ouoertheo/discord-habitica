from dataclasses import dataclass

@dataclass
class RegisterHabiticaAccount:
    discord_user: str
    discord_channel: str
    api_user: str
    api_token: str
    type = "register_user"