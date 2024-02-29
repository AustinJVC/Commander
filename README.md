# Commander - Discord Bot
## About Commander

Commander is a multi-purpose Discord bot developed as a summer project. It offers various functionalities to enhance your server experience:

## Features:

### Music Player:
Commander allows you to play audio from YouTube links directly in voice channels. This feature requires a dedicated system and the installation of ffmpeg libraries on the host machine. Once set up, you can simply submit YouTube links to Commander, and it will:  

1. Download the audio from the YouTube link as an MP3 file.
2. Save the MP3 file locally.
3. Play the MP3 file in the current voice channel.

**Important Note:**

- This feature is currently in an experimental stage and has only been tested locally.
- You might need to adjust the code to specify the correct directory location for your ffmpeg installation.

#### Music Commands:
!join - Joins the voice channel the member is currently in. Will respond with text if the member is not in a voice channel.  
!leave - Leaves the voice channel Commander is currently in.  
!pause - Pauses the audio file currently playing until asked to resume.  
!resume - Resumes the audio file that has been paused.  
!stop - Stops the audio file and dequeues it.  
!play [LINK] - Joins the voice channel the member is current in and plays the requested youtube video.   

### Image Manipulation: 

When someone joins your Discord server, Commander automatically creates and sends a personalized welcome image to the #announcements channel. This image features:

- User's profile picture for a friendly touch.
- Username to make them feel acknowledged.
- Server name to let them know they're in the right place.
- Unique background from a selection you can customize!

**Customizing welcome images:**

Replace existing background images in the "res/welcomeMessages/" folder with your preferred ones.
Update the code with new filenames and adjust the number of available backgrounds for seamless integration.

### Fun:

#### Meme

Sends a popular meme from Reddit.  

Makes an [API](https://meme-api.com/) request, and sends the image url back to the user.  

!meme


#### Cocktails

Recommends a random cocktail to the user. Provides ingredients, photo, and instructions on how to make the drink.  
Makes an [API](https://thecocktaildb.com) request. Formats the information received as a discord embed, and sends the embed back to the user.

!cocktails 

#### Weather


Displays the current temperature of the requested city to the user. Provides daily high, daily low, current temperature, and the flag of the country the city resides.  
Makes an [API](https://openweathermap.org) request for weather, and another API(https://flagsapi.com) request for the regions flag. Formats the information received as a discord embed, and sends the embed back to the user.

!weather [CITY] 

#### 8Ball


Guides the user on how to make the right choices in life.  
Makes an [API](https://eightballapi.com) request for guidance on the topic. Sends the response back to the user as a plain text message.

!8ball [TOPIC] 

#### Bored

Gives the user a recommended activity to cure their boredom.  
Makes an [API](https://www.boredapi.com) request for an activity. Sends the response back to the user as a plain text message.

!bored

#### Joke

Gives the user joke.  
Makes an [API](https://v2.jokeapi.dev/) request for a joke. Sends the response back to the user as a plain text message. Please note, these jokes are hard coded to be dark. This can be fixed by modifying the API request link.

!joke  

## Technical Details:

### Languages Used: 
Python

### Libraries Used:
discord.py  
python-dotenv  
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
