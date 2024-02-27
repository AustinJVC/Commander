import discord
import requests
import welcomeMessage
from discord import File
from discord.ext import commands
from dotenv import load_dotenv
from random import randrange, randint
from easy_pil import Editor, load_image_async, Font

def get_discord_token():
    with open('bot/token.txt', 'r') as file:
        return file.read().strip()

def run_discord_bot():
    load_dotenv()
    DISCORD_TOKEN = get_discord_token()
    
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.tree.command(name="test")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"The test has been completed with `0` errors.")

    @bot.event
    async def on_ready():
        print(f'{bot.user} is now running!')

    @bot.event
    async def on_member_join(member):
        channel = member.guild.system_channel
        profile_image = await load_image_async(str(member.avatar.url))
        await channel.send(f"{member.mention}")
        await channel.send(welcomeMessage.generate_welcome_image(profile_image, member.name, member.guild.name))

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said: [{message.content}]' in: {channel}")

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

        elif user_message.startswith('!weather '):
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

        elif user_message.startswith("!8ball"):
            URL = "https://eightballapi.com/api?question=+&lucky=false"
            response = requests.get(URL).json()
            await message.channel.send(response['reading'])
        
        elif user_message.startswith("!roll"):
            await message.channel.send("You rolled a " + str(randint(1,6)) + "!")
        
        elif user_message.startswith("!help"):
            await message.channel.send("no")

        elif user_message.startswith("!meme"):
            URL = "https://meme-api.com/gimme"
            response = requests.get(URL).json()
            await message.channel.send(response['url'])

        elif user_message.startswith("!bored"):
            URL = "https://www.boredapi.com/api/activity/"
            response = requests.get(URL).json()
            await message.channel.send(response['activity'])

        elif user_message.startswith("!joke"):
            URL = "https://v2.jokeapi.dev/joke/Dark?type=single"
            response = requests.get(URL).json()
            await message.channel.send(response['joke'])

    bot.run(DISCORD_TOKEN)
