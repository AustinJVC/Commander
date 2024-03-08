import requests

def generate_joke():
    """
        Makes a joke API call and returns result to user.

        Topics Blacklist: Religion, Politics, Racism, Sexism.

    Returns:
        response (str): The joke. 
    """
    URL = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=religious,political,racist,sexist&type=single"
    response = requests.get(URL).json()
    return response['joke']