import json

persist = {}

async def get_user_persist():
    """Load from file if not persisted in memory"""
    if 'user' not in persist:
        with open("test\\sample_data\\user_model.json") as fh:
            obj_json = json.load(fh)
    else:
        obj_json = persist['user']
    return obj_json

async def get_user(api_user, api_token):
    obj_json = await get_user_persist()
    
    # 'class' causes deserialization problems
    if 'class' in obj_json['data']['stats']:
        obj_json['data']['stats']['character_class'] = obj_json['data']['stats']['class']
        del obj_json['data']['stats']['class']
    return obj_json

async def get_tasks(api_user, api_token):
    with open("test\\sample_data\\tasks_model.json") as fh:
        obj_json = json.load(fh)
    return obj_json

async def get_party(api_user, api_token):
    with open("test\\sample_data\\party_model.json") as fh:
        obj_json = json.load(fh)
    return obj_json

async def update_user(api_user, api_token, payload):
    obj_json = await get_user_persist()

    # Set the gp in json
    if "stats.gp" in payload:
        obj_json['data']['stats']['gp'] = payload['stats.gp']
    
    # Persist changes
    persist['user'] = obj_json
    return obj_json