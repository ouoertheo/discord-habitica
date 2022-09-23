import json
import os
from persistence.persistence import PersistenceDriverBase

class PersistenceFileDriver(PersistenceDriverBase):
    def __init__(self, base_dir: str) -> None:
        assert(os.path.exists(base_dir))
        self.base_dir = base_dir
        self.file_stores = {
            "user":f"{base_dir}/user.json",
            "integration_user":f"{base_dir}/integration_user.json",
            "group": f"{base_dir}/group.json",
            "webhook": f"{base_dir}/webhook.json"
        }
        "store type mapping to file path"
        self.verify_files()
    
    def load_store(self, store_type):
        with open(self.file_stores[store_type],"r") as store:
            return json.load(store)
    
    def dump_store(self, store_type, payload: dict):
        with open(self.file_stores[store_type],"w") as store:
            json.dump(payload, store)
    
    def verify_files(self):
        "Make sure the persistence files exists"
        for store in self.file_stores:
            if not os.path.exists(self.file_stores[store]):
                with open(self.file_stores[store], 'x') as fh:
                    json.dump({}, fh)

    def create_user(self, id, name, api_user, api_token, group_id=""):
        users: dict = self.load_store("user")
        users[id] = {
            "id": id,
            "name": name,
            "api_user": api_user,
            "api_token": api_token,
            "group_id": group_id
        }
        self.dump_store("user",users)
        return users[id]
            
    
    def get_user_by_id(self, id):
        users: dict = self.load_store("user")
        return users[id]

    def get_user_by_api(self, api_user):
        users: dict = self.load_store("user")
        for user in users.values():
            if user["api_user"] == api_user:
                return user
        raise KeyError(f"User not found with api_user {api_user}")

    def get_user_by_name(self, name):
        users: dict = self.load_store("user")
        for user in users.values():
            if user["name"] == name:
                return user
        raise KeyError(f"User not found with name {name}")

    def get_users_by_group(self, group_id):
        users: dict = self.load_store("user")
        return [user for user in users if user["group_id"] == group_id]

    def update_user_group(self, id, group_id):
        users: dict = self.load_store("user")
        users[id]["group_id"] = group_id
        self.dump_store("user",users)
        return users[id]
    
    def create_integration_user(self, api_user, api_token, group_id):
        integration_users: dict = self.load_store("integration_user")
        integration_users[api_user] = {
            "api_user": api_user,
            "api_token": api_token,
            "group_id": group_id
        }
        self.dump_store("integration_user", integration_users)
        return integration_users[api_user]

    def get_integration_user(self, api_user):
        integration_users: dict = self.load_store("integration_user")
        return integration_users[api_user]

    def update_integration_user_group(self, api_user, group_id):
        integration_users: dict = self.load_store("integration_user")
        integration_users[api_user]["group_id"] = group_id
        self.dump_store("user",integration_users)
        return integration_users[api_user]
    
    def create_group(self, group_id, channel_id="", integration_user_id=""):
        groups: dict = self.load_store("group")
        groups[group_id] = {
            "id": group_id,
            "channel_id": channel_id,
            "integration_user_id": integration_user_id
        }
        self.dump_store("group", groups)
        return groups[group_id]

    def get_group(self, group_id):
        groups: dict = self.load_store("group")
        return groups[group_id]
    
    def update_group(self, group_id, channel_id="", integration_user_id=""):
        groups: dict = self.load_store("group")
        group = groups[group_id]

        if channel_id:
            group["channel_id"] = channel_id

        if integration_user_id:
            group["integration_user_id"] = integration_user_id
        groups["group_id"] = group
        self.dump_store("group", groups)
        return groups[group_id]

    def create_webhook(self, user_id, id, webhook_type, options):
        webhooks: dict = self.load_store("webhook")

        if user_id not in webhooks:
            webhooks[user_id] = {}

        webhooks[user_id][webhook_type] = {
            "id": id,
            "type": webhook_type,
            "user_id": user_id,
            "options": options
        }
        self.dump_store("webhook", webhooks)
        return webhooks[user_id]

    def get_webhooks_by_user(self, user_id):
        webhooks: dict = self.load_store("webhook")
        return webhooks[user_id]
    
    def get_webhook_by_id(self, id):
        webhooks: dict = self.load_store("webhook")
        for user in webhooks.values():
            for webhook in user.values():
                if webhook["id"] == id:
                    return webhook
        raise KeyError(f"webhook_id {id} not found")