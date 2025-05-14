import requests
import logging

logger = logging.getLogger(__name__)

#Makes the API request.
def _make_request(url: str) -> dict | None:
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

    url = "https://meme-api.com/gimme" 
    logger.debug(f"Requesting meme from {url}")
    data = _make_request(url)

    # Just like with the joke API, we block NSFW memes because we don't like NSFW memes and this is on github. Also because this grabs memes from reddit and I'm scared what could potentially come from there.
    if data and 'url' in data and data.get('nsfw') is False:
        meme_url = data['url']
        title = data.get('title', 'Meme')
        logger.info(f"Successfully fetched meme: {title} ({meme_url})")
        return meme_url
    elif data and data.get('nsfw') is True:
        logger.warning(f"Meme API returned NSFW content, skipping. Data: {data}")
        return None 
    else:
        logger.error(f"Failed to fetch or parse meme URL. Data: {data}")
        return None
