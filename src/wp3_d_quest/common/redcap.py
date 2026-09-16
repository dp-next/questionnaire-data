import os
from dataclasses import dataclass
from typing import Any, Literal

import requests


@dataclass
class APIConfig:
    """Configuration for the REDCap API."""

    env_key: str
    url: str


API_CONFIG = APIConfig(
    env_key="REDCAP_OPEN_API_KEY", url="https://open.rsyd.dk/redcap/api/"
)


def get(
    request_data: dict[str, str],
    api_config: APIConfig = API_CONFIG,
) -> requests.Response:
    """Send a request to the REDCap API."""
    token = os.environ.get(api_config.env_key)
    if not token:
        raise RuntimeError(f"{api_config.env_key} environment variable is not set.")

    request_data["token"] = token

    response = requests.post(api_config.url, data=request_data, timeout=60)
    response.raise_for_status()

    return response


def get_json(
    content: Literal["metadata", "repeatingFormsEvents", "formEventMapping"],
) -> Any:
    """Send a request to the REDCap API and return the JSON response."""
    request_data = {
        "content": content,
        "format": "json",
        "returnFormat": "json",
    }
    response = get(request_data)
    return response.json()
