import abc
class PersistenceDriverBase(metaclass=abc.ABCMeta):
    def __init__(self) -> None:
        pass
    
    @abc.abstractmethod
    def create_user(self, api_user, api_token, group_id, discord_id):
        pass

    @abc.abstractmethod
    def get_user(self, api_user):
        pass

    @abc.abstractmethod
    def get_users_by_group(self, group_id):
        pass

    @abc.abstractmethod
    def get_all_users(self):
        pass

    @abc.abstractmethod
    def update_user_group(self, id, group_id):
        pass
    
    @abc.abstractmethod
    def create_group(self, group_id, api_user, api_token, discord_channel_id, api_users=[]):
        pass

    @abc.abstractmethod
    def get_group(self, group_id):
        pass

    @abc.abstractmethod
    def get_all_groups(self):
        pass
    
    @abc.abstractmethod
    def update_group_api_creds(self,group_id, api_user, api_token):
        pass

    @abc.abstractmethod
    def add_group_api_user(self, group_id, api_user):
        pass

    @abc.abstractmethod
    def remove_group_api_user(self, group_id, api_user):
        pass

    @abc.abstractmethod
    def update_group_channel(self, group_id, discord_channel_id):
        pass