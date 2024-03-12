configFile = open("C:/Users/Austin/Desktop/Desktop/CommanderGit/test/bot/config.txt", "r")

def get_token():
    token = configFile.readline().split("=")
    return token[1]

def get_status():
    status = configFile.readline().split("=")
    return status[1]