from persistence.driver_base_new import PersistenceDriverBase
from app.model.app_user import AppUser, UserMap, HabiticaUserLink
from loguru import logger
from app.utils import match_all_in_list, ensure_one

class AppUserExistsException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class HabiticaUserLinkExists(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class AppUserNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class UserMapNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class AppUserService:
    def __init__(self, persistence_driver: PersistenceDriverBase,) -> None:
        self.driver = persistence_driver
        self.store = self.driver.stores.APP_USER
        self.app_users: list[AppUser] = []
        self.init_store()
    
    
    def init_store(self):
        """
        Loads data from persistence
        """
        # Load AppUsers
        app_users_raw = self.driver.list(self.store)
        for app_user_raw in app_users_raw.values():
            app_user = AppUser.load(app_user_raw)
            self.app_users.append(app_user)
                
    def create_app_user(self, app_user_id) -> AppUser:
        if self.get_app_users(app_user_id):
            raise AppUserExistsException(f"App user with id {app_user_id} exists already")
        app_user = AppUser(app_user_id)
        self.app_users.append(app_user)
        self.driver.create(self.store, app_user.dump())
        logger.info(f"Created new AppUser with id: {app_user.id}")
        return app_user

    def get_app_users(self, app_user_id:str="", api_user:str="") -> list[AppUser]:
        """
        Get an AppUser object by discord_id or api_user.
        Raises AppUserNotFoundException if not found.
        """
        matches = match_all_in_list(self.app_users,
                                    id=app_user_id
                                    )
        return matches

    @ensure_one
    def get_app_user(self, app_user_id:str="", api_user:str="") -> AppUser:
        app_user = self.get_app_users(app_user_id, api_user)
        return app_user

    def delete_app_user(self, app_user_id:str):
        app_user = self.get_app_user(app_user_id=app_user_id)
        if not app_user:
            raise AppUserNotFoundException(f"App User with id {app_user_id} not found. Unable to delete.")
        self.app_users.remove(app_user)
        self.driver.delete(self.store, app_user_id)

    
    # Implement HabiticaUserLink
    def add_habitica_user_link(self, app_user_id, api_user, api_token, habitica_user_name, habitica_group_id="") -> UserMap:
        """
        Adds a new Habitica User Link to the AppUser.
        Raises: HabiticaAccountExists
        """
        app_user = self.get_app_user(app_user_id=app_user_id)

        if self.get_habitica_user_links(app_user_id=app_user_id, api_user=api_user):
            raise HabiticaUserLinkExists(f"App user with id {app_user_id} already has Habitica User Link for {api_user}")

        habitica_user = HabiticaUserLink(app_user.id, api_user, api_token, habitica_user_name, habitica_group_id)
        app_user.habitica_user_links.append(habitica_user)

        self.driver.update(self.store, app_user.dump())
        logger.debug(f"Added habitica user {api_user} to App User {app_user_id}")
        return habitica_user

    def get_habitica_user_links(self, app_user_id="", api_user="") -> list[HabiticaUserLink]:
        """
        Searches for HabiticaUserLink objects and returns them. Will return all if no criteria specified.
        Will get all links and search them if app_user_id is not specified.
        """
        # Collect all the habitica users if no app_user_id specified.
        app_user_links = []
        app_users = self.get_app_users(app_user_id)
        for app_user in app_users:
            app_user_links += app_user.habitica_user_links 

        habitica_user_links = match_all_in_list(
            app_user_links,
            app_user_id=app_user_id,
            api_user=api_user
        )
        return habitica_user_links
    
    @ensure_one
    def get_habitica_user_link(self, app_user_id="", api_user="") -> HabiticaUserLink:
        return self.get_habitica_user_links(app_user_id, api_user)

    # ---------------- NOT IMPLEMENTED PROPERLY YET --------------------------
    def get_user_maps(self, app_user_id="", discord_channel: str = "", api_user: str = "") -> list[UserMap]:
        """
        Returns the UserMap object for the given discord channel or habitica api_user. 
        A user map is a discord channel linked to one Habitica Users.

        discord_channel: The discord channel id
        api_user: habitica api user

        Returns None if no UserMap exists
        """        
        app_user = self.get_app_user(app_user_id=app_user_id)
        matches = match_all_in_list(app_user.user_maps,
                                        discord_channel=discord_channel,
                                        app_user_id=app_user_id,
                                        api_user=api_user,
                                        )
        return matches
    
    @ensure_one
    def get_user_map(self, app_user_id="", discord_channel: str = "", api_user: str = "") -> UserMap:
        user_map = self.get_user_maps(app_user_id, discord_channel, api_user)
        return user_map