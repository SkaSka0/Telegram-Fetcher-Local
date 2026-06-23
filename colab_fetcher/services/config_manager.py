import json
from pathlib import Path

from colab_fetcher.utils.logging import logger

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "credentials.json"

ERROR_CREDENTIAL_NOT_FOUND = "Credential file not found at {}"
ERROR_INVALID_JSON = "Invalid JSON format in {}"


def load_credentials():
    if not CONFIG_PATH.exists():
        logger.error(ERROR_CREDENTIAL_NOT_FOUND.format(CONFIG_PATH))
        raise FileNotFoundError(ERROR_CREDENTIAL_NOT_FOUND.format(CONFIG_PATH))

    try:
        with open(CONFIG_PATH, "r") as file:
            logger.info(f"Loaded credentials from {CONFIG_PATH}")
            return json.load(file)
    except json.JSONDecodeError as e:
        logger.error(ERROR_INVALID_JSON.format(CONFIG_PATH) + f": {e}")
        raise ValueError(ERROR_INVALID_JSON.format(CONFIG_PATH))
