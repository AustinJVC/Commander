# Commander - Discord Bot
## About Commander

Commander is a Discord bot created as a personal project during the summer of 2023. It is currently under (somewhat) active development and intended to be a fun and helpful addition to your Discord server.  

Commander currently offers features such as music playback, welcome image generation, various entertainment functionalities, and logging. However, it's important to note that it is still in its very early stages. Please expect potential bugs and limitations as development progresses.  

I welcome feedback and suggestions as I continue to enhance Commander's capabilities. Feel free to reach out through email.

## Quick Start

### Download

Download the Files: Download the bot files onto the system you'll use to host your bot. Many Discord bot hosting services offer a convenient option to automatically pull your files directly from a GitHub repository. This eliminates the need for manual downloading, which we won't cover in this guide as it's a common process.

### Setup

Configuration Required: Once you have downloaded the files, attempting to run the bot directly will likely result in errors. This is because the program requires some configuration adjustments before it can function properly.

#### Directory Changes

Here's a breakdown of the specific directories within the bot's code that you might need to modify:

1. **Config** (bot.py, Line 17): This directory points to your config.txt file. We'll create this file in the next step. Update this path to reflect where you'll store your configuration file.  
2. **Background Images (welcomeImage.py, Line 24)**: This directory points to the location of your background images used for welcome messages. These images should be stored in a subfolder named res/welcomeImages. Update this path to match your image location.  

*Just to let you know, if you're using the music functional branch of the code, please be aware that setting up music playback requires additional configuration beyond the scope of this guide.*

#### Config

We need to create a config file to unlock Commander's full capability. By default I've loaded this file as `/bot/config.txt`, but you can put it wherever as long as you updated the directory. The config file has this format:

```
BOT_TOKEN=your_token_here
BOT_STATUS=your_bot_status
LOG_CHANNEL_ID=log_channel_ID
```

- BOT_TOKEN: Your bot token.
- BOT_STATUS: The status you want on your bot. It will display as "Watching {your_bot_status}"

- LOG_CHANNEL_ID: The channel ID of the logging chat in your server. Commander will automatically send logging information to this channel. Please make sure Commander has access to this channel. 

### Run Script
Boom! You're done. Run the script and everything should work as intended. Send me an email and I'll help you out if that isn't the case.


## Features:

### Music Player:
Commander allows you to play audio from YouTube links directly in voice channels. This feature requires a dedicated system and the installation of ffmpeg libraries on the host machine. Once set up, you can submit YouTube links to Commander, and it will:  

1. Download the audio from the YouTube link as an MP3 file.
2. Save the MP3 file locally.
3. Play the MP3 file in the current voice channel.

**Important Note:**

- This feature works, but is currently in an experimental stage and has only been tested locally. A separate branch has been created with music functionality, but it is no longer updated.
- You might need to adjust the code to specify the correct directory location for your ffmpeg installation.

#### Music Commands:
!join - Joins the voice channel the member is currently in. Commander will respond if the member is not in a voice channel.  
!leave - Leaves the voice channel Commander is currently in.  
!pause - Pauses the audio file currently playing until asked to resume.  
!resume - Resumes the audio file that has been paused.  
!stop - Stops the audio file and dequeues it.  
!play [LINK] - Joins the voice channel the member is currently in and plays the requested YouTube video.   

### Image Manipulation: 

Commander automatically creates and sends a personalized welcome image to the #announcements channel when someone joins your Discord server. This image features:

- User's profile picture for a friendly touch.
- Username to make them feel acknowledged.
- Server name to let them know they're in the right place.
- Unique background from a selection you can customize/

**Customizing welcome images:**

Replace existing background images with your preferred ones in the "res/welcomeMessages/" folder.
Update the code with new filenames and adjust the available backgrounds for seamless integration.

### Fun:

#### Meme

Sends a popular meme from Reddit.  

Makes an [API](https://meme-api.com/) request, and sends the image url back to the user.  

/meme


#### Cocktails

Recommends a random cocktail to the user. Provides ingredients, photos, and instructions on how to make the drink.  
Makes an [API](https://thecocktaildb.com) request. Formats the information received as a discord embed, and sends the embed back to the user.

/cocktails 

#### Weather


Displays the current temperature of the requested city to the user. Provides daily high, daily low, current temperature, and the flag of the country.  
Makes an [API](https://openweathermap.org) request for weather, and another API(https://flagsapi.com) request for the flag of the region. Formats the information received as a discord embed, and sends the embed back to the user.

/weather [CITY] 

#### 8Ball


Guides the user on how to make the right choices in life.  
Makes an [API](https://eightballapi.com) request for guidance on the topic. Sends the response back to the user as a plain text message.

/eightBall [TOPIC] 

#### Bored

Gives the user a recommended activity to cure their boredom.  
Makes an [API](https://www.boredapi.com) request for an activity. Sends the response back to the user as a plain text message.

/bored

#### Joke

Gives the user a joke.  
Makes an [API](https://v2.jokeapi.dev/) request for a joke. Sends the response back to the user as a plain text message. Please note, that these jokes may be hard-coded to be dark depending on the version you are using. This can be fixed by modifying the API request link.

/joke  

#### QOTD

Gives the user the quote of the day (QOTD).

Makes an [API](https://zenquotes.io/api/today) request for the QOTD. Sends the response back to the user as a plain text message. Please note, that the quotes change every day at 00:00UTC.

/qotd

### Logging:

Commander features logging capabilities that will send a message to a specified logging channel. This channel can be edited through the CONFIG.txt file. To change the channel, copy the ID of the channel and place it in the config file.

## Technical Details:

### Languages Used: 
Python

### Libraries Used:
discord.py  
Requests  
easy_pil  
PyNaCl  
youtube-dl (Dedicated host only)  
ffmpeg (Dedicated host only)  

### APIs:
[Cocktails](https://thecocktaildb.com)  
[Weather](https://openweathermap.org)  
[Flags](https://flagsapi.com)  
[8Ball](https://eightballapi.com)  
[Memes](https://meme-api.com/)  
[Bored](https://www.boredapi.com)  
[Jokes](https://v2.jokeapi.dev/)  
