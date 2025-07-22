import discord
from discord import app_commands
from discord.ext import commands
import os
import logging
from services.send_event import send_event

logger = logging.getLogger(__name__)

try:
    from services.weather_service import get_weather_embed
except ImportError:
    import sys
    logger.warning("Could not import weather_service directly, attempting relative import.")
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    try:
        from services.weather_service import get_weather_embed
    except ImportError:
        logging.critical("CRITICAL: Failed to import weather_service. Weather command will not work.", exc_info=True)
        async def get_weather_embed(*args, **kwargs):
             logging.error("get_weather_embed called, but service failed to import.")
             return None

class UtilityCog(commands.Cog, name="Utility"):
    def __init__(self, bot: commands.Bot):
        """
        Initializes the UtilityCog.

        Args:
            bot (commands.Bot): The instance of the Discord bot.
        """

        self.bot = bot
        self.weather_api_key = os.getenv('WEATHER_API_KEY') 
        if not self.weather_api_key:
             logger.warning("WEATHER_API_KEY not found in environment. /weather command will fail if used.")
        else:
             logger.info("UtilityCog initialized successfully.")


    # The big boy weather command. man was I ever proud of this one when i first made this project.
    @app_commands.command(name="weather", description="Get the weather for a specified city.")
    @app_commands.describe(city="The city name (e.g., 'London' or 'London,UK').")
    async def weather(self, interaction: discord.Interaction, city: str):
        """
        Slash command to fetch and display weather information using the weather service.

        Args:
            interaction (discord.Interaction): The interaction object representing the command invocation.
            city (str): The city provided by the user.
        """
        logger.info(f"/weather command used by {interaction.user} (ID: {interaction.user.id}) in server '{interaction.guild.name}' (ID: {interaction.guild.id}) for city: '{city}'")
        await interaction.response.defer(ephemeral=True) 

        # If no API key, get lost. 
        if not self.weather_api_key:
            logger.error(f"Weather command failed: API key is missing. User: {interaction.user}")
            await interaction.followup.send("Sorry, the weather service is not configured correctly (missing API key). Please contact the server owner.", ephemeral=True)
            return

        # Send event to theslow.net
        send_event(
            event_type="weather_command_used",
            description="A user used the /weather command.",
            payload={
                "user_id": str(interaction.user.id),  # safe to log internally
                "username": interaction.user.name,
                "guild_id": str(interaction.guild_id) if interaction.guild_id else "DM",
                "channel_id": str(interaction.channel_id),
            },
            color=0x8c00ff,
            webhook_title="A user used /weather",
            webhook_description= "I hope it's sunny and warm for them! ☀️"
        )

        try:
            weather_embed = get_weather_embed(city, self.weather_api_key)
        except Exception as e:
            logger.error(f"An unexpected error occurred calling get_weather_embed for city '{city}': {e}", exc_info=True)
            weather_embed = None


        if weather_embed:
            if weather_embed.title in ["City Not Found", "API Authentication Error", "Configuration Error", "API Error", "Data Error", "Weather Service Error"]:
                 logger.warning(f"Weather service returned an error embed for '{city}': {weather_embed.title}")
            else:
                 logger.debug(f"Successfully received weather embed for '{city}'.")
            await interaction.followup.send(embed=weather_embed, ephemeral=True)
        else:
            logger.error(f"Weather service returned None for city '{city}'. Sending generic failure message.")
            await interaction.followup.send(f"Sorry, there was an error fetching the weather for '{city}'. Could not connect to the weather service or an unexpected error occurred. Please try again later.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Adds the UtilityCog to the bot.

    Args:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(UtilityCog(bot))
    logger.info("Cog 'UtilityCog' loaded successfully.")

