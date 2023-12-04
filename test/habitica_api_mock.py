import json

async def get_user(api_user, api_token):
    with open("test\\sample_data\\user_model.json") as fh:
        obj_json = json.load(fh)
    
    # 'class' causes deserialization problems
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