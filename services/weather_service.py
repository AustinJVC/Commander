# services/weather_service.py
import discord
import requests
import logging # Import logging

# Get a logger instance for this service file
logger = logging.getLogger(__name__) 

def get_weather_embed(city: str, api_key: str) -> discord.Embed | None: # Renamed WEATHER_API_KEY to api_key for clarity
    """
    Fetches weather data for a city from OpenWeatherMap and formats it into a Discord Embed.

    Args:
        city (str): The requested city for weather information.
        api_key (str): The OpenWeatherMap API key.

    Returns:
        discord.Embed: The formatted weather information in an embed, 
                       an error embed if the city is not found or API key is invalid,
                       or None for other connection/unexpected errors.
    """
    # API Key check (can be done here or in the Cog)
    if not api_key:
        logger.error("Weather service called without an API key.")
        # Return an embed indicating the configuration issue
        return discord.Embed(title="Configuration Error", 
                             description="The Weather API key is not configured. Please contact the bot owner.", 
                             color=discord.Color.red())

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key, # Use the passed api_key
        'units': 'metric' # We aren't from the states, so we're celsius first.
    }
    
    # Log the request attempt using INFO level
    logger.info(f"Requesting weather for '{city}' from OpenWeatherMap...")

    try:
        # Make the API request with a timeout
        response = requests.get(base_url, params=params, timeout=10) 
        # Raise an HTTPError exception for bad status codes (4xx or 5xx)
        response.raise_for_status() 
        data = response.json()

        # --- Data Validation ---
        if 'main' not in data or 'sys' not in data or 'name' not in data:
            # Log the error and the received data for debugging
            logger.error(f"Unexpected API response format for city '{city}'. Data: {data}")
            return discord.Embed(title="API Error", 
                                 description="Well, this is awkward! I received unexpected data from the weather service. Please contact the bot owner!", 
                                 color=discord.Color.orange())

        city_name = data.get('name', city) # Use name from response, fallback to input city
        country_code = data.get('sys', {}).get('country') # Safely get country code
        main_data = data.get('main', {})
        current_temp = main_data.get('temp')
        temp_high = main_data.get('temp_max')
        temp_low = main_data.get('temp_min')

        if current_temp is None or temp_high is None or temp_low is None:
             # Log the error and data
             logger.error(f"Missing temperature data for city '{city}'. Data: {data}")
             return discord.Embed(title="Data Error", 
                                  description=f"Well, this is awkward! I could not retrieve full temperature data for '{city_name}'. Please contact the bot owner!", 
                                  color=discord.Color.orange())

        # --- Data Processing ---
        current_int = int(current_temp)
        high_int = int(temp_high)
        low_int = int(temp_low)

        # --- Embed Creation ---
        embed = discord.Embed(
            title=f"Weather in {city_name}",
            description=f"The current temperature is {current_int}°C ({int(current_int * 1.8 + 32)}°F).",
            color=0x800080 # Purple color
        )

        if country_code:
             flag_url = f"https://flagsapi.com/{country_code}/flat/64.png"
             embed.set_thumbnail(url=flag_url)
        else:
             # Log a warning if country code is missing
             logger.warning(f"Could not get country code for city: {city_name}")

        # Use custom emojis if available, otherwise fallback text/unicode
        up_arrow_emoji = "<:arrow_up:1117699590750224504>" # Replace with your emoji if you have one
        down_arrow_emoji = "<:arrow_down:1117701037361475664>" # Replace with your emoji if you have one

        embed.add_field(
            name="High",
            value=f"{up_arrow_emoji} {high_int}°C ({int(high_int * 1.8 + 32)}°F)",
            inline=True
        )
        embed.add_field(
            name="Low",
            value=f"{down_arrow_emoji} {low_int}°C ({int(low_int * 1.8 + 32)}°F)",
            inline=True
        )

        embed.set_footer(text="Data provided by OpenWeatherMap")
        logger.info(f"Successfully generated weather embed for '{city_name}'.")
        return embed
    
    # --- Error Handling ---
    except requests.exceptions.HTTPError as http_err:
        # Log errors with appropriate levels
        if response.status_code == 404:
            logger.warning(f"City '{city}' not found by OpenWeatherMap API. {http_err}") # Warning level for client error (bad input)
            return discord.Embed(title="City Not Found", 
                                 description=f"Well, this is awkward! Could not find weather data for the city: `{city}`.\nPlease check the spelling and format (e.g., 'London' or 'London,UK').", 
                                 color=discord.Color.red())
        elif response.status_code == 401:
             logger.error(f"Invalid API key or unauthorized access to OpenWeatherMap. {http_err}") # Error level for config issue
             return discord.Embed(title="API Authentication Error", 
                                  description="Well, this is awkward! There's an issue with the weather service API key. Please contact the bot owner!", 
                                  color=discord.Color.red())
        else:
            # Handle other HTTP errors (like 5xx server errors)
            logger.error(f"HTTP error occurred calling OpenWeatherMap for '{city}': {http_err} - Status Code: {response.status_code}", exc_info=True) # Log traceback
            return discord.Embed(title="Weather Service Error", 
                                 description="Well, this is awkward! The weather service returned an error. Please contact the bot owner!", 
                                 color=discord.Color.orange())
            
    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"Request timeout occurred calling OpenWeatherMap for '{city}': {timeout_err}")
        return None # Return None for connection issues, Cog will handle generic message

    except requests.exceptions.RequestException as req_err:
        # Handle other connection errors, etc.
        logger.error(f"Request error occurred calling OpenWeatherMap for '{city}': {req_err}", exc_info=True) # Log traceback
        return None # Return None for connection issues, Cog will handle generic message
        
    except Exception as e:
        # Catch any other unexpected errors during processing
        logger.error(f"An unexpected error occurred in get_weather_embed for city '{city}': {e}", exc_info=True) # Log traceback
        return None # Return None for unexpected errors

