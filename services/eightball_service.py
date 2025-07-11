import requests
import logging

logger = logging.getLogger(__name__)

#Makes the API request.
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

def get_eightball_reading() -> str | None:
    url = "https://eightballapi.com/api"
    # The API requires a question, but because I don't know what they do with the questions, we are just putting a placeholder in. And lucky because false confidence works. 
    params = {'question': 'Will I succeed?', 'lucky': 'true'} 
    logger.debug(f"Requesting 8ball reading from {url}")
    data = _make_request(url, params=params)

    if data and 'reading' in data:
        reading = data['reading']
        logger.info(f"Successfully fetched 8ball reading: {reading}")
        return reading
    else:
        logger.error(f"Failed to fetch or parse 8ball reading. Data: {data}")
        return None
