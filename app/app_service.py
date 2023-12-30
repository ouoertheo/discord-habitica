from persistence.driver_base_new import PersistenceDriverBase
from loguru import logger
import asyncio

from habitica.habitica_service import HabiticaService, HabiticaUser
from app.bank_service import BankService
from app.app_user_service import AppUserService, AppUserNotFoundException
import habitica.habitica_api

import app.events.event_service as event_service
from app.events import app_events, discord_events, bank_events

class AppService:
    def __init__(self, habitica_api: habitica.habitica_api,
                  persistence_driver: PersistenceDriverBase,
                  app_user_service: AppUserService,
                  bank_service: BankService,
                  habitica_service: HabiticaService
                ) -> None:
        self.habitica_api = habitica_api
        self.app_user_service = app_user_service
        self.bank_service = bank_service
        self.habitica_service = habitica_service
        self.driver = persistence_driver
        self.store = self.driver.stores.APP_USER


    ###############
    ## App Users ##
    ###############
    async def register_habitica_account(self, app_user_id, app_user_name, discord_channel, api_user, api_token):
        """
        Create a new AppUser if it doesnt exist. Register and link the Habitica user to the Discord channel id.
        """
        logger.info(f"Received user registration for habitica user {api_user} in channel {discord_channel} ")

        # Create the AppUser if it does not exist yet, then create the Habitica User
        # NOTE: This is where I choose to bind the Discord User Id as the identifier for App Users
        app_user = self.app_user_service.get_app_user(app_user_id=app_user_id)
        if not app_user:
            app_user = self.app_user_service.create_app_user(app_user_id, app_user_name) 

        # Call Habitica for the User so we have a name to create the habitica user link with.
        habitica_user = await self.habitica_service.get_user(api_user, api_token)
        user_name = habitica_user.profile.name
        group_id = habitica_user.party._id

        # Register the Habitica User Link to the App User
        self.app_user_service.add_habitica_user_link(app_user.id, api_user, api_token, user_name, group_id)
    
    async def get_status_message(self, app_user_id):
        app_user_id = str(app_user_id)
        message = ""
        user_links = self.app_user_service.get_habitica_user_links(app_user_id=app_user_id)
        habitica_users: list[HabiticaUser] = []
        for link in user_links:
            habitica_users.append(await self.habitica_service.get_user(link.api_user, link.api_token))
        
        message += f"Habitica Users\n"
        for user in habitica_users:
            message += f"    {user.profile.name}: Level {user.stats.lvl} {user.stats.character_class} 🪙{int(user.stats.gp)} ♥️{int(user.stats.hp)}/{user.stats.maxHealth} ⭐{user.stats.exp}/{user.stats.toNextLevel} 💠{user.stats.mp}/{user.stats.maxMP}\n"
        message += f"Bank Accounts\n"
        bank_accounts = self.bank_service.get_accounts(app_user_id=app_user_id)
        for account in bank_accounts:
            owner = [o.profile.name for o in habitica_users if o.id == account.habitica_user_id][0]
            message += f"    {owner}: {account.name} {account.account_type}: {account.balance}\n"
        return message


