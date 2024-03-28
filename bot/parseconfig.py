configFile = open("bot/config.txt", "r")

token = configFile.readline().split("=")[1]
status = configFile.readline().split("=")[1]
log_channel =  configFile.readline().split("=")[1]

def get_token():
    return token

def get_status():
    return status

def get_log_channel():
    return log_channel
