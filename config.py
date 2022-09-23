import dotenv, os
import logging

logger = logging.getLogger(__name__)
from persistence.file_driver import PersistenceFileDriver

dotenv.load_dotenv(".env")
ENVIRONMENT = os.getenv("ENVIRONMENT")
HABITICA_BASE_URL = os.getenv("HABITICA_BASE_URL")
SERVER_PORT = os.getenv("SERVER_PORT")
STORE_DIR = os.getenv("STORE_DIR")

DRIVER = PersistenceFileDriver(STORE_DIR)

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

LOCAL_SERVER_URL = f"{EXTERNAL_SERVER_URL}:{EXTERNAL_SERVER_PORT}/habitica"