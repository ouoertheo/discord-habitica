
import json
import aiohttp
import config as cfg
import time

logger = cfg.logging.getLogger(__name__)

x_client = '3006b14d-b672-4fc6-ab54-3da40dd1c55e-discord-habitica'

class CircuitBreaker:
    def __init__(self) -> None:
        self.current_value = 0
        self.limit_value = cfg.HABITICA_API_CIRCUIT_BREAKER_COUNT
        self.interval_ms = 5000
        self.last_interval = time.time()
        self.call_history = []

    def is_open(self):
        '''
        Track timestamp of each call in a list, and if there's too many entries as defined by HABITICA_API_CIRCUIT_BREAKER_COUNT
        in the past interval_ms (5s by default), then open the circuit breaker.

        Return true if the circuit breaker is open, indicating we should no longer send API calls
        '''
        state = False
        now = int(time.time())
        self.call_history.append(now)
        calls_in_range = [c for c in self.call_history if c < now-self.interval_ms]
        if len(calls_in_range) > self.limit_value:
            # Circuit breaker is opened
            logger.warning(f"Circuit breaker open: {len(calls_in_range)} calls in last {self.interval_ms}")
            self.call_history = calls_in_range
            state = True
        return state 

circuit_breaker = CircuitBreaker()

async def get(api_user, api_token, command_path):
    if circuit_breaker.is_open():
        raise Exception(f"Circuit breaker open, call stopped: {command_path}")
    auth_headers = {
        "x-client": x_client,
        "x-api-user": api_user,
        "x-api-key": api_token
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(cfg.HABITICA_API_BASE_URL+command_path, headers=auth_headers) as response:
            response_json = json.loads(await response.text())
            if response.status >= 400:
                message = f"HabiticaAPI: {command_path} {response.status} {await response.text()}"
                logger.error(message)
                raise Exception(message)

    return response_json

async def post(api_user, api_token, command_path, payload: dict):
    if circuit_breaker.is_open():
        raise Exception(f"Circuit breaker open, call stopped: {command_path}")
    auth_headers = {
        "x-client": x_client,
        "x-api-user": api_user,
        "x-api-key": api_token
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            cfg.HABITICA_API_BASE_URL+command_path,
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
    if circuit_breaker.is_open():
        raise Exception(f"Circuit breaker open, call stopped: {command_path}")
    auth_headers = {
        "x-client": x_client,
        "x-api-user": api_user,
        "x-api-key": api_token
    }

    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{cfg.HABITICA_API_BASE_URL}{command_path}/{id}",
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