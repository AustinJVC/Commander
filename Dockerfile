FROM python:3.9-slim

WORKDIR /usr/src/app

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy your bot code and any additional files
COPY . .

# Set the command to run your bot script
CMD [ "python", "bot.py" ]