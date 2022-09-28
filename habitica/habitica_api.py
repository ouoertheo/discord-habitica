
import json
import aiohttp
import logging
import dotenv, os
import config

logger = logging.getLogger(__name__)


async def get(api_user, api_token, command_path):
    auth_headers = {
        "x-api-user": api_user,
        "x-api-key": api_token
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(config.HABITICA_API_BASE_URL+command_path, headers=auth_headers) as response:
            response_json = json.loads(await response.text())
            if response.status >= 400:
                message = f"HabiticaAPI: {command_path} {response.status} {await response.text()}"
                logger.error(message)
                raise Exception(message)

    return response_json

async def post(api_user, api_token, command_path, payload: dict):
    auth_headers = {
        "x-api-user": api_user,
        "x-api-key": api_token
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            config.HABITICA_API_BASE_URL+command_path,
            headers=auth_headers,
            json=payload
        ) as response:
            response_json = json.loads(await response.text())
            if response.status >= 400:
                message = f"HabiticaAPI: {command_path} {response.status} {response.text()}"
                logger.error(message)
                raise Exception(message)

    return response_json

async def delete(api_user, api_token, command_path, id: dict):
    auth_headers = {
        "x-api-user": api_user,
        "x-api-key": api_token
    }

    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{config.HABITICA_API_BASE_URL}{command_path}/{id}",
            headers=auth_headers,
        ) as response:
            response_json = json.loads(await response.text())
            if response.status >= 400:
                message = f"HabiticaAPI: {command_path} {response.status} {response.text()}"
                logger.error(message)
                raise Exception(message)

    return response_json

async def get_user(api_user, api_token):
    return await get(api_user, api_token, "/user")

async def get_party(api_user, api_token):
    return await get(api_user, api_token, "/groups/party")

async def get_webhooks(api_user, api_token):
    return await get(api_user, api_token, "/user/webhook")
    
async def create_webhook(api_user, api_token, payload):
    return await post(api_user, api_token, "/user/webhook", payload)

async def delete_webhook(api_user, api_token, id):
    return await delete(api_user, api_token, "/user/webhook", id)