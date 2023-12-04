import asyncio, json

ignore_list = [
    "type",
    "date",
    "startDate",
    "createdAt",
    "updatedAt",
    "nextDue",
    "dateCompleted"
]
def cleanse_data(data, exclude_keys=[]):
    if isinstance(data, str):
        return "data"
    elif isinstance(data, (int, float)):
        return 0
    elif isinstance(data, list):
        return [cleanse_data(item, exclude_keys) for item in data]
    elif isinstance(data, dict):
        cleansed_data = {}
        for key, value in data.items():
            if key in exclude_keys:
                cleansed_data[key] = value  # Exclude specific keys from cleansing
            else:
                cleansed_data[key] = cleanse_data(value, exclude_keys)
        return cleansed_data
    else:
        return data  # Return unchanged for other data types

with open("E:\\Code\\discord-habitica\\test\\sample_data\\taskActivity-reward.json",'r') as fh:
    data = json.load(fh)
print(cleanse_data(data,ignore_list))

async def generate_sample_data():
    generate_dict = {
        "":""
    }