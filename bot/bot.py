import discord
from discord import File
from discord.ext import commands, tasks
import os
import requests
from dotenv import load_dotenv
import youtube_dl
import asyncio
import ffmpeg
from random import randrange, randint
from easy_pil import Editor, load_image_async, Font

def run_discord_bot():
    load_dotenv()
    DISCORD_TOKEN = 'TOKEN'
    
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    youtube_dl.utils.bug_reports_message = lambda: ''
    ytdl_format_options = {
        'format': 'bestaudio/best',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',  # binded to ipv4
        'outtmpl': 'res/audio/%(title)s.%(ext)s'
    }
    ffmpeg_options = {
        'options': '-vn'
    }
    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
    
    class YTDLSource(discord.PCMVolumeTransformer):
        def __init__(self, source, *, data, volume=0.5):
            super().__init__(source, volume)
            self.data = data
            self.title = data.get('title')
            self.url = ""

        @classmethod
        async def from_url(cls, url, *, loop=None, stream=False):
            loop = loop or asyncio.get_event_loop()
            try:
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
                if 'entries' in data:
                    # take first item from a playlist
                    data = data['entries'][0]
                filename = data['title'] if stream else ytdl.prepare_filename(data)
                return filename
            except Exception as e:
                print(e)
                return None
    @bot.tree.command(name="test")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"The test has been completed with `0` errors.")

    @bot.command(name='play')
    async def play_song(ctx, *, url):
        url = ctx.message.content.split(' ')[1]
        try:
            if ctx.author.voice:
                # Existing code...
                async with ctx.typing():
                    await ctx.send("**Fetching audio:** This may take a moment!")
                    filename = await YTDLSource.from_url(url, loop=bot.loop)
                    if filename is not None:
                        print("Playing executable")
                        voice_client.play(discord.FFmpegPCMAudio(executable="D:\PATH_Programs/ffmpeg", source=filename))
                        print("Executable playing")
                        title = filename.split('\\')
                        title = str(title[2]).lower()
                        title = title.replace('_', ' ').split('.m4')
                        title = title[0].split('.web')
                        title = str(title[0]).title()
                        await ctx.send(f'**Now playing:** {title}')
                    else:
                        await ctx.send("Failed to fetch audio.")
            else:
                await ctx.send("You are not connected to a voice channel.")
        except Exception as e:
            print("Error occurred:", e)
            traceback.print_exc()  # Print the full traceback
            await ctx.send("An error occurred while trying to play the song.")
    @bot.event
    async def on_ready():
        print(f'{bot.user} is now running!')

    @bot.event
    async def on_member_join(member):
        channel = member.guild.system_channel
        background_image = ["road.jpg", "sky.jpg", "skyline.jpg"]
        background_number = randrange(3)
        background = Editor("res/welcomeMessages/" + background_image[background_number])
        profile_image = await load_image_async(str(member.avatar.url))

        profile = Editor(profile_image).resize((300, 300)).circle_image()

        poppins = Font.poppins(size=100, variant='bold')

        poppins_small = Font.poppins(size=60, variant='light')

        background.paste(profile, (800, 200))
        background.ellipse((800, 200), 300, 300, outline='white', stroke_width=5)

        background.text((960, 600), f"Welcome to {member.guild.name}", color='white', font=poppins, align='center')

        background.text((960,750), f"{member.name}", color='white', font=poppins_small, align='center')

        file = File(fp=background.image_bytes, filename='road.jpg')
        print("file is file")
        print("sending file")
        await channel.send(f"{member.mention}")
        await channel.send(file=file)

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said: [{message.content}]' in: {channel}")

        if user_message == '!join':
            if not message.author.voice:
                
                embed=discord.Embed(title="You’re kidding, right? You never show up. You aren't even there right now.", description="Join a server voice, then ask me again.", color=0xee00ff)
                embed.set_author(name="Join?")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1117363244282159114/1117363306705981591/enter.jpg")
                
                await message.channel.send(embed=embed)

            else:
                channel = message.author.voice.channel
                await channel.connect()
       
        if user_message.startswith("!play"):
            url = user_message.split(' ')[1]
            
            # Create a dummy Context object
            print("Creating content")
            content = f"!play {url}"
            print("Content created")
            dummy_message = message
            print("Dummy message created")
            dummy_message.content = content
            print("Dummy message content created")

            print("Invoking bot.process_commands")
            await bot.process_commands(dummy_message)  # Invoke the command through the bot


        if user_message == '!pause':
            voice_client = message.guild.voice_client
            if voice_client.is_playing():
                await voice_client.pause()
            else:   
                embed=discord.Embed(title="I’m already paused. Do you want me to freeze too?", description="But you can unpause me with !resume", color=0xee00ff)
                embed.set_author(name="Pause?")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1117363244282159114/1117363307406430290/pause.jpg")
                await message.channel.send(embed=embed)

        if user_message == '!resume':
            voice_client = message.guild.voice_client
            if voice_client.is_paused():
                await voice_client.resume()
            else:
                embed=discord.Embed(title="Resume what? Are you hallucinating?", description="I either don't have anything to resume, or I'm currently playing something for you.", color=0xee00ff)
                embed.set_author(name="Resume?")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1117363244282159114/1117363307712622642/play.jpg")
                await message.channel.send(embed=embed)

        if user_message == '!leave':
            voice_client = message.guild.voice_client
            if voice_client.is_connected():
                await voice_client.disconnect()
            else:
                embed=discord.Embed(title="I’m already gone. You can’t hurt me anymore.", description="I'm not there! If you want me to join do !join", color=0xee00ff)
                embed.set_author(name="Leave?")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1117363244282159114/1117363307104452648/exit.jpg")
                await message.channel.send(embed=embed)

        if user_message == '!stop':
            voice_client = message.guild.voice_client
            if voice_client.is_playing():
                await voice_client.stop()
                
            else:
                embed=discord.Embed(title="There is no music. Only silence. And pain.", description="I can't stop the music since I have nothing playing. If you'd like to play something, add it with !play {url}", color=0xee00ff)
                embed.set_author(name="Stop?")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1117363244282159114/1117363308043976874/stop.jpg")
                await message.channel.send(embed=embed)
       
       
        if user_message == "!cocktails":

            URL = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
            
            valid_drink = False
            response = requests.get(URL)
            data = response.json()
            
            while not valid_drink:
                tempdata = response.json()
                ing1 = tempdata['drinks'][0]['strIngredient1']
                ing2 = tempdata['drinks'][0]['strIngredient2']
                ing3 = tempdata['drinks'][0]['strIngredient3']

                mes1 = tempdata['drinks'][0]['strMeasure1']
                mes2 = tempdata['drinks'][0]['strMeasure2']
                mes3 = tempdata['drinks'][0]['strMeasure3']

                if (ing1 != None) and (ing2 != None) and (ing3 != None) and (mes1 != None) and (mes2 != None) and (mes3 != None):
                    data = response.json()
                    valid_drink = True
                else:
                    response = requests.get(URL)
                
            name = data['drinks'][0]['strDrink'].lower()
            category= data['drinks'][0]['strCategory'].lower()
            instructions = data['drinks'][0]['strInstructions']
            
            ing1 = data['drinks'][0]['strIngredient1']
            ing2 = data['drinks'][0]['strIngredient2']
            ing3 = data['drinks'][0]['strIngredient3']

            mes1 = data['drinks'][0]['strMeasure1']
            mes2 = data['drinks'][0]['strMeasure2']
            mes3 = data['drinks'][0]['strMeasure3']
            
            image = data['drinks'][0]['strDrinkThumb']

            an = 'an'
            if (category[0] != 'a') and (category[0] != 'e') and (category[0] != 'o') and (category[0] != 'i') and (category[0] != 'u'):
                an = 'a'

            embed=discord.Embed(title=f"{name.title()}", 
                                description=f"**-**{mes1} {ing1} \n **-** {mes2} {ing2} \n **-** {mes3} {ing3}\n ... And more \n \n \n **Instructions:** \n {instructions}", color=0xee00ff)
            embed.set_author(name=f"{category.title()}")
            embed.set_thumbnail(url=f"{image}")
            
            await message.channel.send(embed=embed)
            await bot.process_commands(message)

        if user_message == '!musichelp':
                
            embed=discord.Embed(title="Need help with Commander Music Bot? Here is a list of the most useful commands!", color=0xee00ff)
            embed.set_author(name="Help!")
            embed.add_field(name="!play {URL}", value="Plays a specified video from YouTube, and takes it's URL as a parameter.", inline=True)
            embed.add_field(name="!join", value="Commander will join the voice channel of which the author is currently in.", inline=True)
            embed.add_field(name="!leave", value="Commander leaves the voice channel he is currently occupying.", inline=True)
            embed.add_field(name="!pause", value="Pauses the current song, making it easy to come back to later on.", inline=True)
            embed.add_field(name="!resume", value="Resumes the current song ", inline=True)
            embed.add_field(name="!stop", value="Turns off the music, but Commander will remain in the channel.", inline=True)
            await message.channel.send(embed=embed)

        if user_message.startswith('!weather '):
            city = user_message.split(' ')
            city = city[1]
            key = '86cbf0be7a3752741f43640e6b06ea79'

            URL=f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric'
            response = requests.get(URL)
            data = response.json()
            code = data['sys']['country']
            current = int(data['main']['temp'])
            high = int(data['main']['temp_max'])
            low = int(data['main']['temp_min'])

            embed=discord.Embed(title=f"{city}", description=f"The current temperature in {city} is {current}°C!", color=0xee00ff)
            embed.set_thumbnail(url=f"https://flagsapi.com/{code}/flat/64.png")
            embed.set_author(name="Weather")
            embed.add_field(name="*High*", value=f"<:arrow_up:1117699590750224504> {high}°C", inline=False)
            embed.add_field(name="*Low*", value=f"<:arrow_down:1117701037361475664> {low}°C", inline=True)
            await message.channel.send(embed=embed)

        if user_message.startswith("!8ball"):
            URL = "https://eightballapi.com/api?question=+&lucky=false"
            response = requests.get(URL).json()
            await message.channel.send(response['reading'])
        
        if user_message.startswith("!roll"):
            await message.channel.send("You rolled a " + str(randint(1,6)) + "!")
        
        if user_message.startswith("!help"):
            await message.channel.send("no")

        if user_message.startswith("!meme"):
            URL = "https://meme-api.com/gimme"
            response = requests.get(URL).json()
            await message.channel.send(response['url'])

        if user_message.startswith("!bored"):
            URL = "https://www.boredapi.com/api/activity/"
            response = requests.get(URL).json()
            await message.channel.send(response['activity'])

        if user_message.startswith("!bored"):
            URL = "https://v2.jokeapi.dev/joke/Dark?type=single"
            response = requests.get(URL).json()
            await message.channel.send(response['joke'])

    bot.run(DISCORD_TOKEN)
