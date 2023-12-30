import dotenv, os
from persistence.file_driver_new import PersistenceFileDriver
from loguru import logger
dotenv.load_dotenv(".env")

# All configs below inherit from .env file

# Optional configs in .env
ENVIRONMENT = os.getenv("ENVIRONMENT") or "DEV"
HABITICA_API_BASE_URL = os.getenv("HABITICA_BASE_URL") or "https://habitica.com/api/v3"
SERVER_PORT = os.getenv("SERVER_PORT") or 8952
STORE_DIR = os.getenv("STORE_DIR") or "store"
HABITICA_API_CIRCUIT_BREAKER_COUNT = 30 # How many calls can be made in a 5 second period.


TEST_HABITICA_API_USER = os.getenv("TEST_HABITICA_USER_ID")
TEST_HABITICA_API_TOKEN = os.getenv("TEST_HABITICA_API_TOKEN")
# Required configs in .env
if ENVIRONMENT == "PROD":
    logger.info("Using prod configs")
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    EXTERNAL_SERVER_URL = os.getenv("EXTERNAL_SERVER_URL")
    EXTERNAL_SERVER_PORT = os.getenv("EXTERNAL_SERVER_PORT")
elif ENVIRONMENT == "DEV":
    logger.info("Using dev configs")
    DISCORD_TOKEN = os.getenv("TEST_DISCORD_TOKEN")
    EXTERNAL_SERVER_URL = os.getenv("DEV_EXTERNAL_SERVER_URL")
    EXTERNAL_SERVER_PORT = os.getenv("DEV_EXTERNAL_SERVER_PORT")
else:
    logger.critical(f"Value: {ENVIRONMENT} for ENVIRONMENT env specified. Must be DEV or PROD")

# Convenience stuff.
DRIVER = PersistenceFileDriver(STORE_DIR)
LOCAL_SERVER_URL = f"{EXTERNAL_SERVER_URL}:{EXTERNAL_SERVER_PORT}/habitica"