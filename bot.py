#External Imports
import discord
from discord import app_commands
from discord.ext import commands
import datetime
from dotenv import load_dotenv
import os

#Local imports
from  cogs import cocktailEmbed
from  cogs import fetchWeather
from  cogs import welcomeImage
from  cogs.eightBallReading import reading
from  cogs import rollDice
from  cogs import fetchMeme
from  cogs import giveActivity
from  cogs import fetchJoke
from  cogs import fetchQOTD
from  cogs import ordinal

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if DISCORD_BOT_TOKEN is None:
    print("Error: DISCORD_BOT_TOKEN not found.")
    print("Make sure you have a .env file with DISCORD_BOT_TOKEN=YOUR_TOKEN")
    exit()

DISCORD_BOT_STATUS = os.getenv('DISCORD_BOT_STATUS')
if DISCORD_BOT_STATUS is None:
    print("Warning: STATUS not found.")
    print("Make sure you have a .env file with DISCORD_BOT_STATUS=YOUR_STATUS. Proceeding with no status.")
    DISCORD_BOT_STATUS = " "

LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')
if LOG_CHANNEL_ID is None:
    print("Warning: LOG_CHANNEL_ID not found.")
    print("Make sure you have a .env file with LOG_CHANNEL_ID=YOUR_LOG_CHANNEL_ID. Proceeding without logging capabilites.")

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
if WEATHER_API_KEY is None:
    print("Warning: WEATHER_API_KEY not found.")
    print("Make sure you have a .env file with WEATHER_API_KEY=YOUR_WEATHER_API_KEY. Proceeding without weather capabilites.")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = bot.tree

@bot.event
async def on_ready():
    """
        Print to console bot has gone online, then sync commands with the Discord API and set bot status.
    """
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.tree.sync()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{str(DISCORD_BOT_STATUS)}"))

@bot.tree.command(name="echo", description="Echoes a message.")
@app_commands.describe(message="The message to echo.")
async def echo(inter: discord.Interaction, message: str) -> None:
    print(f"Command used:\nUsername: {inter.user.name}\nCommand: echo\nChannel ID: {inter.channel.id}\nChannel: {inter.channel.name}\nServer ID: {inter.guild.id}\nServer: {inter.guild.name}\n\n")
    """
        Echos the users message back to them.

    Args:
        interaction (discord.Interaction): Discord interaction.
        message (str): Message to be echoed back.
    """
    await inter.response.send_message(message)
    


@bot.tree.command(name="weather", description="Get the weather for the specified city. To specify country, simply use the format \'Toronto,CA\'")
@app_commands.describe(city="City")
async def weather(inter: discord.Interaction, city: str) -> None:
    print(f"Command used:\nUsername: {inter.user.name}\nCommand: weather\nChannel ID: {inter.channel.id}\nChannel: {inter.channel.name}\nServer ID: {inter.guild.id}\nServer: {inter.guild.name}\n\n")
    """  Sends the current, high, and low temperatures for the requested city.

    Args:
        interaction (discord.Interaction): Discord interaction.
        city (str): City for the requested weather."""
    await inter.response.send_message(embed=fetchWeather.weather(city, WEATHER_API_KEY))


@bot.tree.command(name="cocktail", description="Get a random cocktail suggestion")
async def cocktail(inter: discord.Interaction) -> None:
    print(f"Command used:\nUsername: {inter.user.name}\nCommand: cocktail\nChannel ID: {inter.channel.id}\nChannel: {inter.channel.name}\nServer ID: {inter.guild.id}\nServer: {inter.guild.name}\n\n")
    """
        Sends the user a random cocktail.

    Args:
        inter (discord.Interaction): Discord interaction.
    """
    await inter.response.send_message(embed=cocktailEmbed.cocktail())

@bot.tree.command(name="welcome", description="Test generate welcome message")
async def welcome(inter: discord.Interaction) -> None:
    print(f"Command used:\nUsername: {inter.user.name}\nCommand: welcome\nChannel ID: {inter.channel.id}\nChannel: {inter.channel.name}\nServer ID: {inter.guild.id}\nServer: {inter.guild.name}\n\n")
    """
        Tests the welcome image generation process and sends it.

    Args:
        inter (discord.Interaction): Discord interaction.
    """
    print(f"ATTEMPTING WELCOME IMAGE: \nIMG:{inter.user.avatar} \nNAME:{inter.user.name}\nSERVER_NAME:{inter.guild.name}")
    file = await welcomeImage.generate_image(inter.user.avatar, inter.user.name, inter.guild.name)
    await inter.response.send_message(file=file)

@bot.tree.command(name="eightball", description="Get an eight ball reading!")
@app_commands.describe(question="What would you like to ask?")
async def eightBallReading(interaction: discord.Interaction, question: str) -> None:
    print(f"Command used:\nUsername: {interaction.user.name}\nCommand: eightball\nChannel ID: {interaction.channel.id}\nChannel: {interaction.channel.name}\nServer ID: {interaction.guild.name}\nServer: {interaction.guild.name}")
    """
        Sends the user an eightball reading for the issue that troubles them.

    Args:
        interaction (discord.Interaction): Discord interaction.
        question (str): Question to receive the 8ball reading (Has no affect).
    """
    message = reading()
    await interaction.response.send_message(message)

@bot.tree.command(name="roll", description="Roll a number 1-6!")
async def roll_die(inter: discord.Interaction) -> None:
    print(f"Command used:\nUsername: {inter.user.name}\nCommand: roll\nChannel ID: {inter.channel.id}\nChannel: {inter.channel.name}\nServer ID: {inter.guild.id}\nServer: {inter.guild.name}\n\n")
    """
        Sends the user a random number between 1-6.

    Args:
        inter (discord.Interaction): Discord interaction.
    """
    await inter.response.send_message(f"You rolled a {rollDice.result()}!")

@bot.tree.command(name="help", description="Provide assistance in using commands!")
async def help(inter: discord.Interaction) -> None:
    print(f"Command used:\nUsername: {inter.user.name}\nCommand: help\nChannel ID: {inter.channel.id}\nChannel: {inter.channel.name}\nServer ID: {inter.guild.id}\nServer: {inter.guild.name}\n\n")
    """
        Has no real purpose. Sends the user a michael scott meme.

    Args:
        inter (discord.Interaction): Discord interaction.
    """
    await inter.response.send_message("https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNDMydTU3N2NhNDFqZXY5a2l4amtxY3I3Z2U5c3lxc3Q3bTN6cTR0ZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/8vUEXZA2me7vnuUvrs/giphy.gif")

@bot.tree.command(name="meme", description="Get a current meme!")
async def meme(inter: discord.Interaction) -> None:
    print(f"Command used:\nUsername: {inter.user.name}\nCommand: meme\nChannel ID: {inter.channel.id}\nChannel: {inter.channel.name}\nServer ID: {inter.guild.id}\nServer: {inter.guild.name}\n\n")
    """
        Sends the user a random meme from reddit.

    Args:
        inter (discord.Interaction): Discord interaction.
    """
    await inter.response.send_message(fetchMeme.get_meme())

@bot.tree.command(name="bored", description="Get an activity to do while bored!")
async def bored(inter: discord.Interaction) -> None:
    print(f"Command used:\nUsername: {inter.user.name}\nCommand: bored\nChannel ID: {inter.channel.id}\nChannel: {inter.channel.name}\nServer ID: {inter.guild.id}\nServer: {inter.guild.name}\n\n")
    """
        Sends the user a random activity.

    Args:
        inter (discord.Interaction): Discord interaction.
    """
    await inter.response.send_message(giveActivity.generate_activity())

@bot.tree.command(name="joke", description="Get a joke!")
async def joke(inter: discord.Interaction) -> None:
    print(f"Command used:\nUsername: {inter.user.name}\nCommand: join\nChannel ID: {inter.channel.id}\nChannel: {inter.channel.name}\nServer ID: {inter.guild.id}\nServer: {inter.guild.name}\n\n")
    """
        Sends the user a random joke.

    Args:
        inter (discord.Interaction): Discord interaction.
    """
    await inter.response.send_message(fetchJoke.generate_joke())

@bot.tree.command(name="qotd", description="Get the quote of the day!")
async def qotd(inter: discord.Interaction) -> None:
    print(f"Command used:\nUsername: {inter.user.name}\nCommand: qotd\nChannel ID: {inter.channel.id}\nChannel: {inter.channel.name}\nServer ID: {inter.guild.id}\nServer: {inter.guild.name}\n\n")
    """
        Sends the user the quote of the day.

    Args:
        inter (discord.Interaction): Discord interaction.
    """
    await inter.response.send_message(fetchQOTD.generate_qotd())

@bot.event
async def on_message_edit(before, after):
    timestamp = datetime.datetime.now().strftime(f"%A, %B {ordinal.get_ordinal(datetime.datetime.now().day)} %Y, at %I:%M %p")
    footer = f"ID: {after.id} - {timestamp}"

    channelID = bot.get_channel(int(LOG_CHANNEL_ID))
    if before.content != after.content:
        embed=discord.Embed(title=f"Message edited in #{after.channel.name}.", color=0xFFBF00)
        embed.set_author(name=f"{after.author.name}", url=f"https://discordlookup.com/user/{after.author.id}", icon_url=f"{after.author.avatar}")
        embed.add_field(name="Before:", value=f"{before.content}", inline=False)
        embed.add_field(name="After:", value=f"{after.content}", inline=False)
        embed.set_footer(text=f"{footer}")
        await channelID.send(embed=embed)

@bot.event
async def on_message_delete(message):
    timestamp = datetime.datetime.now().strftime(f"%A, %B {ordinal.get_ordinal(datetime.datetime.now().day)} %Y, at %I:%M %p")
    footer = f"ID: {message.author.id} - {timestamp}"

    channelID = bot.get_channel(int(LOG_CHANNEL_ID))
    embed=discord.Embed(title=f"Message deleted in #{message.channel.name}.", color=0xFF0000)
    embed.set_author(name=f"{message.author.name}", url=f"https://discordlookup.com/user/{message.author.id}", icon_url=f"{message.author.avatar}")
    embed.add_field(name="Deleted Message:", value=f"{message.content}", inline=False)
    embed.add_field(name="Message ID:", value=f"{message.id}", inline=True)
    embed.set_footer(text=f"{footer}")
    await channelID.send(embed=embed)


@bot.event
async def on_voice_state_update(member, before, after):
    channelID = bot.get_channel(int(LOG_CHANNEL_ID))
    timestamp = datetime.datetime.now().strftime(f"%A, %B {ordinal.get_ordinal(datetime.datetime.now().day)} %Y, at %I:%M %p")
    footer = f"ID: {member.id} - {timestamp}"

    if before.channel is None:
        embed=discord.Embed(title=f"Member joined a voice channel.", color=0x56FF00)
        embed.set_author(name=f"{member.name}", url=f"https://discordlookup.com/user/{member.id}", icon_url=f"{member.avatar}")
        embed.add_field(name="Channel:", value=f"{after.channel}", inline=False)
        embed.set_footer(text=f"{footer}")
        await channelID.send(embed=embed)
    elif after.channel is None:
        embed=discord.Embed(title=f"Member left a voice channel.", color=0xFF0000)
        embed.set_author(name=f"{member.name}", url=f"https://discordlookup.com/user/{member.id}", icon_url=f"{member.avatar}")
        embed.add_field(name="Channel:", value=f"{before.channel}", inline=False)
        embed.set_footer(text=f"{footer}")
        await channelID.send(embed=embed)
    else:
        embed=discord.Embed(title=f"Member changed voice channels.", color=0xFFBF00)
        embed.set_author(name=f"{member.name}", url=f"https://discordlookup.com/user/{member.id}", icon_url=f"{member.avatar}")
        embed.add_field(name="Before:", value=f"#{before.channel}", inline=False)
        embed.add_field(name="+After:", value=f"#{after.channel}", inline=False)
        embed.set_footer(text=f"{footer}")
        await channelID.send(embed=embed)

@bot.event
async def on_member_join(member):
    """
        Calls welcomeImage to generate a welcome image with the users avatar, username, and server name. then sends a message to the server log.

    Args:
        member (member): Member who has joined the server.
    """
    channel = member.guild.system_channel
    print(f"ATTEMPTING IMAGE: \n IMG:{member.avatar.url} \n NAME:{member.name}\n SERVER_NAME:{member.guild.name}") #Prints status to console with users avatar, username, and server name
    file = await welcomeImage.generate_image(member.avatar.url, member.name, member.guild.name) #Calls image generator to create the image.
    await channel.send(f"{member.mention}") #Sends a message mentioning the user.
    await channel.send(file=file) #Sends the welcome image as a file.


    join_position = member.guild.member_count + 1 
    timestamp = datetime.datetime.now().strftime(f"%A, %B {ordinal.get_ordinal(datetime.datetime.now().day)} %Y, at %I:%M %p")
    created = member.created_at.strftime(f"%B {ordinal.get_ordinal(member.created_at.day)} %Y")
    footer = f"ID: {member.id} - {timestamp}"

    channelID = bot.get_channel(int(LOG_CHANNEL_ID))
    embed=discord.Embed(title="Member Joined.", color=0x56FF00)
    embed.set_author(name=f"{member.name}", url=f"https://discordlookup.com/user/{member.id}", icon_url=f"{member.avatar}")
    embed.add_field(name=f"{member.name} (joined {ordinal.get_ordinal(join_position)}).", value=f"Account created {created}.", inline=True)
    embed.set_footer(text=f"{footer}")
    await channelID.send(embed=embed)

@bot.event
async def on_member_remove(member):
    timestamp = datetime.datetime.now().strftime(f"%A, %B {ordinal.get_ordinal(datetime.datetime.now().day)} %Y, at %I:%M %p")
    joined = member.joined_at.strftime(f"%B {ordinal.get_ordinal(member.joined_at.day)} %Y")
    footer = f"ID: {member.id} - {timestamp}"

    channelID = bot.get_channel(int(LOG_CHANNEL_ID))
    embed=discord.Embed(title="Member Left.", color=0xff0000)
    embed.set_author(name=f"{member.name}", url=f"https://discordlookup.com/user/{member.id}", icon_url=f"{member.avatar}")
    embed.add_field(name=f"{member.name} joined on {joined}.", value=f"", inline=True)
    embed.set_footer(text=f"{footer}")
    await channelID.send(embed=embed)

@bot.event
async def on_user_update(before, after):
    print(f"NAME: {before.name}, {after.name}")
    print(f"GLOBAL: {before.global_name}, {after.global_name}")
    timestamp = datetime.datetime.now().strftime(f"%A, %B {ordinal.get_ordinal(datetime.datetime.now().day)} %Y, at %I:%M %p")
    footer = f"ID: {after.id} - {timestamp}"


    channelID = bot.get_channel(int(LOG_CHANNEL_ID))
    if before.name != after.name:
        embed=discord.Embed(title="Member Name Update.", color=0xFF00EF)
        embed.set_author(name=f"{before.name}", url=f"https://discordlookup.com/user/{after.id}", icon_url=f"{before.avatar}")
        embed.add_field(name=f"Before:", value=f"{before.name}", inline=False)
        embed.add_field(name=f"+ After:", value=f"{after.name}", inline=False)
        embed.set_footer(text=f"{footer}")
        await channelID.send(embed=embed)
    
    elif before.global_name != after.global_name:
        embed=discord.Embed(title="Member Global Name Update.", color=0xFF00EF)
        embed.set_author(name=f"{before.name}", url=f"https://discordlookup.com/user/{after.id}", icon_url=f"{before.avatar}")
        embed.add_field(name=f"Before:", value=f"{before.global_name}", inline=False)
        embed.add_field(name=f"+ After:", value=f"{after.global_name}", inline=False)
        embed.set_footer(text=f"{footer}")
        await channelID.send(embed=embed)

    else:
        embed=discord.Embed(title="Avatar Update.", color=0xFF00EF)
        embed.set_thumbnail(url=f"{after.avatar}")
        embed.set_author(name=f"{before.name}", url=f"https://discordlookup.com/user/{after.id}", icon_url=f"{before.avatar}")
        embed.set_footer(text=f"{footer}")
        await channelID.send(embed=embed)


bot.run(DISCORD_BOT_TOKEN)