import requests
import logging

logger = logging.getLogger(__name__)

def _make_request(url: str, params: dict = None) -> dict | None:
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        if 'application/json' in response.headers.get('Content-Type', ''):
            return response.json()
        else:
            logger.error(f"Non-JSON response from {url}: {response.headers.get('Content-Type')}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None

def get_joke() -> str | None:
    """Fetches a joke from JokeAPI."""
    # Using 'Any' category but blacklisting flags for safety
    url = "https://v2.jokeapi.dev/joke/Any"
    params = {
        'blacklistFlags': 'racist,sexist',
        'type': 'single'
    }
    logger.debug(f"Requesting joke from {url}")
    data = _make_request(url, params=params)

    if data and data.get('error') is False and 'joke' in data:
        joke_text = data['joke']
        logger.info("Successfully fetched joke.")
        return joke_text
    elif data and data.get('error') is True:
         logger.error(f"JokeAPI returned an error: {data.get('message')}")
         return None
    else:
        logger.error(f"Failed to fetch or parse joke. Data: {data}")
        return None
