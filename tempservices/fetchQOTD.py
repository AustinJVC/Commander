import requests

def generate_qotd():
    """
        Makes a joke API call and returns result to user.

        Topics Blacklist: Religion, Politics, Racism, Sexism.

    Returns:
        response (str): The joke. 
    """
    URL = "https://zenquotes.io/api/today"
    response = requests.get(URL).json()
    return f"{response[0]['q']}\n-{response[0]['a']}"