import requests

def generate_activity():
    """
    
        Makes an activity API call and returns result to user.

    Returns:
        response (str): The activity. 
    """
    URL = "https://www.boredapi.com/api/activity/"
    response = requests.get(URL).json()
    return response['activity']