# services/activity_service.py
import requests
import logging

logger = logging.getLogger(__name__)

def _make_request(url: str) -> dict | None:
    """Helper to make requests and handle basic errors."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        if 'application/json' in response.headers.get('Content-Type', ''):
            return response.json()
        else:
            logger.error(f"Non-JSON response from {url}: {response.headers.get('Content-Type')}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None

def get_activity() -> str | None:
    """Fetches a random activity from the Bored API."""
    url = "https://bored-api.appbrewery.com/random"
    logger.debug(f"Requesting activity from {url}")
    data = _make_request(url)

    if data and 'activity' in data:
        activity = data['activity']
        logger.info(f"Successfully fetched activity: {activity}")
        return activity
    else:
        logger.error(f"Failed to fetch or parse activity. Data: {data}")
        return None
