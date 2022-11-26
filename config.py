import dotenv, os
import logging
import logging.config
import json
from persistence.file_driver import PersistenceFileDriver

with open("logging.json","r") as log_config:
    log_config = json.loads(log_config.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)

dotenv.load_dotenv(".env")

# All configs below inherit from .env file

# Optional configs in .env
ENVIRONMENT = os.getenv("ENVIRONMENT") or "DEV"
HABITICA_API_BASE_URL = os.getenv("HABITICA_BASE_URL") or "https://habitica.com/api/v3"
SERVER_PORT = os.getenv("SERVER_PORT") or 8952
STORE_DIR = os.getenv("STORE_DIR") or "store"
HABITICA_API_CIRCUIT_BREAKER_COUNT = 30 # How many calls can be made in a 5 second period.

# Required configs in .env
if ENVIRONMENT == "PROD":
    logger.info("Using prod configs")
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    HABITICA_API_USER = os.getenv("PROXY_HABITICA_USER_ID")
    HABITICA_API_TOKEN = os.getenv("PROXY_HABITICA_API_TOKEN")
    EXTERNAL_SERVER_URL = os.getenv("EXTERNAL_SERVER_URL")
    EXTERNAL_SERVER_PORT = os.getenv("EXTERNAL_SERVER_PORT")
elif ENVIRONMENT == "DEV":
    logger.info("Using dev configs")
    DISCORD_TOKEN = os.getenv("TEST_DISCORD_TOKEN")
    HABITICA_API_USER = os.getenv("TEST_PROXY_HABITICA_USER_ID")
    HABITICA_API_TOKEN = os.getenv("TEST_PROXY_HABITICA_API_TOKEN")
    EXTERNAL_SERVER_URL = os.getenv("DEV_EXTERNAL_SERVER_URL")
    EXTERNAL_SERVER_PORT = os.getenv("DEV_EXTERNAL_SERVER_PORT")
else:
    logger.critical(f"Value: {ENVIRONMENT} for ENVIRONMENT env specified. Must be DEV or PROD")

# Convenience stuff. Don
DRIVER = PersistenceFileDriver(STORE_DIR)
LOCAL_SERVER_URL = f"{EXTERNAL_SERVER_URL}:{EXTERNAL_SERVER_PORT}/habitica"