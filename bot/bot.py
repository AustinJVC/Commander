#External Imports
import discord
from discord import app_commands
from discord.ext import commands

#Local imports
import cocktailEmbed
import weatherEmbed
import welcomeImage
from eightBallReading import reading
import rollDice
import fetchMeme
import giveActivity
import fetchJoke

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = bot.tree

def get_discord_token():
    with open('bot/token.txt', 'r') as file:
        return file.read().strip()

@bot.event
async def on_ready():
    """
        Print to console bot has gone online, then sync commands with the Discord API
    """
    print(f"Logged in as {bot.user} (ID: {bot.user.id})") #Print bot status
    await bot.tree.sync()  # Sync commands to API
    # Setting `Watching ` status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="DieselBarbiieTTV"))

@bot.event
async def on_member_join(member):
    """
        Calls welcomeImage to generate a welcome image with the users avatar, username, and server name.

    Args:
        member (member): Member who has joined the server.
    """
    channel = member.guild.system_channel
    print(f"ATTEMPTING IMAGE: \n IMG:{member.avatar.url} \n NAME:{member.name}\n SERVER_NAME:{member.guild.name}") #Prints status to console with users avatar, username, and server name
    file = await welcomeImage.generate_image(member.avatar.url, member.name, member.guild.name) #Calls image generator to create the image.
    await channel.send(f"{member.mention}") #Sends a message mentioning the user.
    await channel.send(file=file) #Sends the welcome image as a file.

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

@bot.tree.command(name="weather", description="Get the weather for the specified city.")
@app_commands.describe(city="City")
async def weather(inter: discord.Interaction, city: str) -> None:
    print(f"Command used:\nUsername: {inter.user.name}\nCommand: weather\nChannel ID: {inter.channel.id}\nChannel: {inter.channel.name}\nServer ID: {inter.guild.id}\nServer: {inter.guild.name}\n\n")
    """
        Sends the current, high, and low temperatures for the requested city.

    Args:
        interaction (discord.Interaction): Discord interaction.
        city (str): City for the requested weather.
    """
    await inter.response.send_message(embed=weatherEmbed.weather(city))

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

bot.run(get_discord_token())