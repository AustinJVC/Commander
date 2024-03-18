import requests

def generate_joke():
    """
        Makes a joke API call and returns result to user.

        Topics Blacklist: Religion, Politics, Racism, Sexism.

    Returns:
        response (str): The joke. 
    """
    URL = "https://v2.jokeapi.dev/joke/Dark?type=single"
    response = requests.get(URL).json()
    return response['joke']