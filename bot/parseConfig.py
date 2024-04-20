configFile = open("config.txt", "r")

token_line = configFile.readline().strip()
token = token_line.split("=")[1]

status_line = configFile.readline().strip()
status = status_line.split("=")[1]

log_channel_line = configFile.readline().strip()
log_channel = log_channel_line.split("=")[1]

configFile.close()

print(f"Config read as:\nToken: {token}\nStatus: {status}\nLogs: {log_channel}")


def get_token():
    return token

def get_status():
    return status

def get_log_channel():
    return log_channel
