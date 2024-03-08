import requests

def reading():
    """
        Makes an eightball API call and returns result to user.

    Returns:
        response (str): The eight ball reading
    """
    URL = "https://eightballapi.com/api?question=+&lucky=true"
    response = requests.get(URL).json()
    return response['reading']