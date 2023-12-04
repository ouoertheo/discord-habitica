
class SendDiscordMessage:
    type = "send_discord_message"
    def __init__(self, discord_channel:str, message:str) -> None:
        self.discord_channel = discord_channel
        self.message = message
    
class ReceiveDiscordMessage:
    type = "receive_discord_message"
    def __init__(self, discord_message) -> None:
        self.discord_message = discord_message
