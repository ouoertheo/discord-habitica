import logging
from habitica.habitica_user import HabiticaUser

logger = logging.getLogger(__name__)

class HabiticaBot(commands.Bot):
    def __init__(self, **options: Any) -> None:

        self.habitica_user: HabiticaUser = None
        self.channel = None
        self.cache = RegistrationCache()
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(".", intents=intents, **options)

    async def on_ready(self):
        logger.info("Discord client ready. Intializing Habitica connection...")
        self.habitica_user = HabiticaUser(cfg.HABITICA_API_USER, cfg.HABITICA_API_TOKEN)
        await self.habitica_user.fetch_user_details()
        await self.habitica_user.verify_webhooks()
        logger.info(f"Bot connected to Habitica using user: {self.habitica_user.user_name}")
        logger.info(f"Available webhooks: {self.habitica_user.webhooks}")
        
    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        await self.process_commands(message)
        if message.content.startswith(".register"):
            async with message.channel.typing():
                registration_result = self.register_channel_command(message.clean_content, message.channel.id)
                await message.channel.send(registration_result)
        # if message.content == ".test":
        #     await message.channel.send("Hello World", components=[
        #         Button(style=discord.ButtonStyle.primary, label="Press me", custom_id="my_custom_id")
        #     ])
    
    def register_channel_command(self, message: str, channel_id: str):
        try:
            group_id = message.split()[1]
        except Exception:
            return ".register requires group_id argument"
        if self.channel:
            return f"Already registered habitica group_id: {group_id}"
        else:
            try:
                self.channel = self.cache.get_channel(group_id)
                return f"Already registered habitica group_id: {group_id}"
            except KeyError:
                self.cache.save_channel(channel_id, group_id)
                return f"Registered habitica group_id: {self.habitica_user.group_id}"
    
    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        logger.exception(sys.exc_info())
        raise Exception(sys.exc_info())

    
    async def handle_webhook(self, payload):
        try:
            if payload["chat"]["uuid"] == "system":
                user_name = "System"
            else:
                user_name = payload["chat"]["username"]
            user_id = payload["chat"]["uuid"]
            group_id = payload["chat"]["groupId"]
            message = payload["chat"]["unformattedText"]

            if not self.channel:
                channel_id = self.cache.get_channel(group_id)
                self.channel = self.get_channel(channel_id)

            if self.habitica_user.group_id == group_id:
                async with self.channel.typing():
                    logger.debug(f"Sent message:\"{user_name}: {message}\"")
                    await self.channel.send(f"{user_name}: {message}")
        except Exception as err:
            logger.error(err)

    def register_channel(self, channel_id, group_id):
        """
        Checks REGISTERED_CHANNELS cache for existing group:channel mapping. If its not there, create it.
        returns: channel that is registered
        """
        cache: dict[str,str]
        self.channel = self.get_channel(channel_id)
        group_id = self.habitica_user.group_id

    async def on_interaction(self, interaction: discord.Interaction):
        pass

    async def setup_hook(self) -> None:
        # Sync the application command with Discord.
        await self.tree.sync()