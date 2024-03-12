configFile = open("res/bot/config.txt", "r")

def get_token():
    token = configFile.readline().split("=")
    return token[1]

def get_status():
    status = configFile.readline().split("=")
    return status[1]