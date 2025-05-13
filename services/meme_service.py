# services/meme_service.py
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

def get_meme_url() -> str | None:
    """Fetches a random meme URL from meme-api."""
    # Consider specifying a subreddit if desired: url = "https://meme-api.com/gimme/wholesomememes"
    url = "https://meme-api.com/gimme" 
    logger.debug(f"Requesting meme from {url}")
    data = _make_request(url)

    # Check for essential keys and ensure NSFW is false (if API provides it)
    if data and 'url' in data and data.get('nsfw') is False:
        meme_url = data['url']
        title = data.get('title', 'Meme')
        logger.info(f"Successfully fetched meme: {title} ({meme_url})")
        return meme_url
    elif data and data.get('nsfw') is True:
        logger.warning(f"Meme API returned NSFW content, skipping. Data: {data}")
        # Optionally retry here, but be careful about loops
        return None 
    else:
        logger.error(f"Failed to fetch or parse meme URL. Data: {data}")
        return None
