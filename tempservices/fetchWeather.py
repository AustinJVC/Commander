import discord
import requests

def weather(city, WEATHER_API_KEY):
    """
        Takes a user inputted city, sends an API call for the weather at that city, then a flag call for the country that city is in. Takes all that, and records a discord embed
        including the flag, daily high, low, and current temperatures.

    Args:
        city (str): The requested city temperatures
        WEATHER_API_KEY (str): The API key for the weather api.
    Returns:
        Embed (discord.Embed): The weather formatted in a discord embed.
    """

    #Make the API call
    URL=f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric'
    response = requests.get(URL)
    data = response.json()

    #Save the weather info as variables
    code = data['sys']['country']
    current = int(data['main']['temp'])
    high = int(data['main']['temp_max'])
    low = int(data['main']['temp_min'])

    #Formats as an embed. 
    embed=discord.Embed(title=f"{city}", description=f"The current temperature in {city} is {current}°C ({int(current * 1.8 + 32)}°F)!", color=0xee00ff)
    embed.set_thumbnail(url=f"https://flagsapi.com/{code}/flat/64.png")
    embed.set_author(name="Weather")
    embed.add_field(name="*High*", value=f"<:arrow_up:1117699590750224504> {high}°C ({int(high * 1.8 + 32)}°F)", inline=False)
    embed.add_field(name="*Low*", value=f"<:arrow_down:1117701037361475664> {low}°C ({int(low * 1.8 + 32)}°F)", inline=True)

    return embed