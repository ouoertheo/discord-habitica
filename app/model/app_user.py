from dataclasses import dataclass, asdict, field
from dacite import from_dict
from loguru import logger

# TODO: Create an app_user_service and move all methods to that (from here and app_service)

@dataclass
class HabiticaUserLink:
    "A light version of a Habitica User"
    app_user_id: str
    api_user: str
    api_token: str
    name: str = ""
    group_id: str = ""
    cache_dirty: bool = False

@dataclass
class UserMap:
    """ Bind a set of Habitica users to a Discord Channel"""
    app_user_id: str
    discord_channel: str
    api_user: str
    api_token: str

@dataclass
class AppUser:
    id: str
    name: str
    user_maps: list[UserMap] = field(default_factory=list)
    habitica_user_links: list[HabiticaUserLink] = field(default_factory=list)

    def dump(self):
        model = {
            "id": self.id,
            "name": self.name,
            "user_maps": [asdict(user_map) for user_map in self.user_maps],
            "habitica_user_links": [asdict(habitica_user) for habitica_user in self.habitica_user_links]
        }
        return model
    
    @staticmethod
    def load(model):
        return from_dict(AppUser, model)