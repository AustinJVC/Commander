import requests

def get_meme():
    """
        Makes a meme API call and returns result to user.

    Returns:
        response (str): The meme image URL. 
    """
    URL = "https://meme-api.com/gimme"
    response = requests.get(URL).json()
    return response['url']