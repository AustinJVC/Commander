configFile = open("config.txt", "r")

token = configFile.readline().split("=")[1].strip()
status = configFile.readline().split("=")[1].strip()
log_channel =  configFile.readline().split("=")[1].strip()

print(f"Config read as:\nToken: {token}\nStatus: {status}\nLogs: {log_channel}")


def get_token():
    return token

def get_status():
    return status

def get_log_channel():
    return log_channel
