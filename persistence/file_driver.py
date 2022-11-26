import json
import os
from persistence.persistence import PersistenceDriverBase

class PersistenceFileDriver(PersistenceDriverBase):
    def __init__(self, base_dir: str) -> None:
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
            
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

    def create_user(self, api_user, api_token, group_id, discord_user_id):
        users: dict = self.load_store("user")
        users[api_user] = {
            "api_user": api_user,
            "api_token": api_token,
            "group_id": group_id,
            "discord_id": discord_user_id
        }
        self.dump_store("user",users)
        return users[api_user]

    def get_user(self, api_user):
        users: dict = self.load_store("user")
        for user in users.values():
            if user["api_user"] == api_user:
                return user
        raise KeyError(f"User not found with api_user {api_user}")

    def get_users_by_group(self, group_id):
        users: dict = self.load_store("user")
        return [user for user in users if user["group_id"] == group_id]

    def get_all_users(self):
        users: dict = self.load_store("user")
        return users

    def update_user_group(self, api_user, group_id):
        users: dict = self.load_store("user")
        users[api_user]["group_id"] = group_id
        self.dump_store("user",users)
        return users[api_user]
    
    def create_group(self, group_id, api_user, api_token, discord_channel_id, api_users=[]):
        groups: dict = self.load_store("group")
        groups[group_id] = {
            "group_id": group_id,
            "api_user": api_user,
            "api_token": api_token,
            "discord_channel_id": discord_channel_id,
            "api_users": api_users
        }
        self.dump_store("group", groups)
        return groups[group_id]

    def get_group(self, group_id):
        groups: dict = self.load_store("group")
        return groups[group_id]
        
    def get_all_groups(self):
        groups: dict = self.load_store("group")
        return groups

    def update_group_api_creds(self, group_id, api_user, api_token):
        groups: dict = self.load_store("group")
        group = groups[group_id]
        group["api_user"] = api_user
        group["api_token"] = api_token
        self.dump_store("group", groups)
        return group
    
    def add_group_api_user(self, group_id, api_user):
        groups: dict = self.load_store("group")
        group = groups[group_id]
        group["api_users"].append(api_user)
        self.dump_store("group", groups)
        return group

    def remove_group_api_user(self, group_id, api_user):
        groups: dict = self.load_store("group")
        group = groups[group_id]
        for i, user in enumerate(group["api_users"]):
            if user == api_user:
                group["api_users"].pop(i)
        self.dump_store("group", groups)
        return group

    def update_group_channel(self, group_id, discord_channel_id):
        groups: dict = self.load_store("group")
        group = groups[group_id]
        group["discord_channel_id"] = discord_channel_id
        self.dump_store("group", groups)
        return group