# cogs/utility.py (Assuming this file is in the 'cogs' directory)
import discord
from discord import app_commands
from discord.ext import commands
import os
# import services # Not typically needed if importing specific functions
import logging # Import logging

# Import the specific service function
try:
    from services.weather_service import get_weather_embed
except ImportError:
    # Fallback for different project structures or running script directly
    import sys
    logger.warning("Could not import weather_service directly, attempting relative import.") # Log warning
    sys.path.append(os.path.join(os.path.dirname(__file__), '..')) # Add project root to path
    try:
        from services.weather_service import get_weather_embed
    except ImportError:
        # Log a critical error if the service cannot be imported
        logging.critical("CRITICAL: Failed to import weather_service. Weather command will not work.", exc_info=True)
        # Define a placeholder function to prevent NameError later if import fails
        async def get_weather_embed(*args, **kwargs):
             logging.error("get_weather_embed called, but service failed to import.")
             return None

# Get a logger instance for this Cog file
logger = logging.getLogger(__name__)

class UtilityCog(commands.Cog, name="Utility"): # Added name="Utility" for clarity
    """
    Cog containing various utility commands like weather lookup.
    """
    def __init__(self, bot: commands.Bot):
        """
        Initializes the UtilityCog.

        Args:
            bot (commands.Bot): The instance of the Discord bot.
        """
        self.bot = bot
        # Fetch the API key when the Cog is loaded
        self.weather_api_key = os.getenv('WEATHER_API_KEY') 
        if not self.weather_api_key:
             # Log a warning if the key is missing - the command checks again before running
             logger.warning("WEATHER_API_KEY not found in environment. /weather command will fail if used.")
        else:
             # Log successful initialization at INFO level
             logger.info("UtilityCog initialized successfully.")


    @app_commands.command(name="weather", description="Get the weather for a specified city.")
    @app_commands.describe(city="The city name (e.g., 'London' or 'London,UK').")
    async def weather(self, interaction: discord.Interaction, city: str):
        """
        Slash command to fetch and display weather information using the weather service.

        Args:
            interaction (discord.Interaction): The interaction object representing the command invocation.
            city (str): The city provided by the user.
        """
        # Log command usage with user and guild info
        logger.info(f"/weather command used by {interaction.user} (ID: {interaction.user.id}) in server '{interaction.guild.name}' (ID: {interaction.guild.id}) for city: '{city}'")
        
        # Defer response - ephemeral=True makes the thinking message and final response only visible to the user
        await interaction.response.defer(ephemeral=True) 

        # Check if the API key was loaded during initialization
        if not self.weather_api_key:
            # Log the error
            logger.error(f"Weather command failed: API key is missing. User: {interaction.user}")
            await interaction.followup.send("Sorry, the weather service is not configured correctly (missing API key). Please contact the server owner.", ephemeral=True)
            return

        # Call the service function to get the embed
        # Add error handling around the service call itself
        try:
            weather_embed = get_weather_embed(city, self.weather_api_key)
        except Exception as e:
            logger.error(f"An unexpected error occurred calling get_weather_embed for city '{city}': {e}", exc_info=True)
            weather_embed = None # Ensure embed is None if the call fails

        # Check the result from the service
        if weather_embed:
            # Check if the service returned a specific error embed (like 404)
            if weather_embed.title in ["City Not Found", "API Authentication Error", "Configuration Error", "API Error", "Data Error", "Weather Service Error"]:
                 logger.warning(f"Weather service returned an error embed for '{city}': {weather_embed.title}")
            else:
                 logger.debug(f"Successfully received weather embed for '{city}'.") # DEBUG level for success details
            # Send the embed (success or error embed from service)
            await interaction.followup.send(embed=weather_embed, ephemeral=True) # Keep ephemeral consistent
        else:
            # If get_weather_embed returned None (connection error, unexpected error in service)
            logger.error(f"Weather service returned None for city '{city}'. Sending generic failure message.")
            await interaction.followup.send(f"Sorry, there was an error fetching the weather for '{city}'. Could not connect to the weather service or an unexpected error occurred. Please try again later.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Adds the UtilityCog to the bot.

    Args:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(UtilityCog(bot))
    # Log successful loading of the Cog
    logger.info("Cog 'UtilityCog' loaded successfully.")

