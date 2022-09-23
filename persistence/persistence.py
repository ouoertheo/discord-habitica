import abc
class PersistenceDriverBase(metaclass=abc.ABCMeta):
    def __init__(self) -> None:
        pass
    
    @abc.abstractmethod
    def create_user(self, id, name, api_user, api_token, group_id=""):
        pass

    @abc.abstractmethod
    def get_user_by_id(self, id):
        pass

    @abc.abstractmethod
    def get_user_by_api(self, api_user):
        pass

    @abc.abstractmethod
    def get_user_by_name(self, name):
        pass

    @abc.abstractmethod
    def get_users_by_group(self, group_id):
        pass

    @abc.abstractmethod
    def update_user_group(self, id, group_id):
        pass
    
    @abc.abstractmethod
    def create_integration_user(self, api_user, api_token, group_id):
        pass

    @abc.abstractmethod
    def get_integration_user(self, api_user):
        pass

    @abc.abstractmethod
    def update_integration_user_group(self, api_user, group_id):
        pass  
    
    @abc.abstractmethod
    def create_group(self, group_id, channel_id="", integration_user_id=""):
        pass

    @abc.abstractmethod
    def get_group(self, group_id):
        pass

    @abc.abstractmethod
    def update_group(self, group_id, channel_id="", integration_user_id=""):
        pass

    @abc.abstractmethod
    def create_webhook(self, user_id, id, type, options):
        pass

    @abc.abstractmethod
    def get_webhooks_by_user(self, user_id):
        pass

    @abc.abstractmethod
    def get_webhook_by_id(self, id):
        pass

