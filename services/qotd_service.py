import requests
import logging

logger = logging.getLogger(__name__)

#Makes the API request.
def _make_request(url: str) -> list | None:
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

def get_qotd() -> str | None:
    """Fetches the quote of the day from ZenQuotes."""
    url = "https://zenquotes.io/api/today"
    logger.debug(f"Requesting QOTD from {url}")
    data = _make_request(url)

    if data and isinstance(data, list) and len(data) > 0 and 'q' in data[0] and 'a' in data[0]:
        quote = data[0]['q']
        author = data[0]['a']
        formatted_quote = f"> {quote}\n> \n> *- {author}*"
        logger.info(f"Successfully fetched QOTD by {author}")
        return formatted_quote
    else:
        logger.error(f"Failed to fetch or parse QOTD. Data: {data}")
        return None
