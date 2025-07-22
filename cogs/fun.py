import discord
from discord import app_commands
from discord.ext import commands
import logging
from services.send_event import send_event
from services.cocktail_service import get_cocktail_embed
from services.eightball_service import get_eightball_reading
from services.joke_service import get_joke
from services.meme_service import get_meme_url
from services.qotd_service import get_qotd
from services.activity_service import get_activity


# Get a logger for this Cog
logger = logging.getLogger(__name__)

class FunCog(commands.Cog):
    """
    Cog containing fun, miscellaneous commands like jokes, memes, etc.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("FunCog initialized.")

    # Our cocktail command because i know a lot of alcoholics
    @app_commands.command(name="cocktail", description="Get a random cocktail suggestion.")
    async def cocktail(self, interaction: discord.Interaction):
        """Sends a random cocktail recipe."""
        logger.info(f"Cocktail command triggered by {interaction.user.name}")
        await interaction.response.defer() 
        
        cocktail_embed = get_cocktail_embed()
        
        # Send event to theslow.net
        send_event(
            event_type="cocktail_command_used",
            description="A user used the /cocktail command.",
            payload={
                "user_id": str(interaction.user.id),  # safe to log internally
                "username": interaction.user.name,
                "guild_id": str(interaction.guild_id) if interaction.guild_id else "DM",
                "channel_id": str(interaction.channel_id),
            },
            color=0x8c00ff,
            webhook_title="A user used /cocktail",
            webhook_description= "Someone’s feeling thirsty. 🍸"
        )

        if cocktail_embed:
            await interaction.followup.send(embed=cocktail_embed)
        else:
            logger.error("Failed to get cocktail embed from service.")
            await interaction.followup.send("Sorry, I couldn't mix a cocktail suggestion right now. Please try again later.", ephemeral=True)

    # Eightball command because jesus take the wheel
    @app_commands.command(name="eightball", description="Ask the magic 8-ball a question!")
    @app_commands.describe(question="The yes/no question you want to ask.")
    async def eightball(self, interaction: discord.Interaction, question: str):
        """Provides a magic 8-ball reading."""
        logger.info(f"Eightball command triggered by {interaction.user.name} with question: '{question}'")
        await interaction.response.defer()
        
        reading = get_eightball_reading()
        
        # Send event to theslow.net
        send_event(
            event_type="eightball_command_used",
            description="A user used the /eightball command.",
            payload={
                "user_id": str(interaction.user.id),  # safe to log internally
                "username": interaction.user.name,
                "guild_id": str(interaction.guild_id) if interaction.guild_id else "DM",
                "channel_id": str(interaction.channel_id),
            },
            color=0x8c00ff,
            webhook_title="A user used /eightball",
            webhook_description= "Someone’s lacking the confidence to make their own decisions. 🎱"
        )

        if reading:
            await interaction.followup.send(f"You asked: \"{question}\"\nThe Magic 8-Ball says: **{reading}**")
        else:
            logger.error("Failed to get 8ball reading from service.")
            await interaction.followup.send("Sorry, the Magic 8-Ball seems cloudy right now. Please try again later.", ephemeral=True)

    # Joke command because we still haven't found a better joke than your life. 
    @app_commands.command(name="joke", description="Get a random SFW joke.")
    async def joke(self, interaction: discord.Interaction):
        """Sends a random joke."""
        logger.info(f"Joke command triggered by {interaction.user.name}")
        await interaction.response.defer()
        
        joke_text = get_joke()
        
        # Send event to theslow.net
        send_event(
            event_type="joke_command_used",
            description="A user used the /joke command.",
            payload={
                "user_id": str(interaction.user.id),  # safe to log internally
                "username": interaction.user.name,
                "guild_id": str(interaction.guild_id) if interaction.guild_id else "DM",
                "channel_id": str(interaction.channel_id),
            },
            color=0x8c00ff,
            webhook_title="A user used /joke",
            webhook_description= "Someone’s not funny enough to impress their crush, hope I helped. 🤣"
        )

        if joke_text:
            await interaction.followup.send(joke_text)
        else:
            logger.error("Failed to get joke from service.")
            await interaction.followup.send("Sorry, I couldn't think of a joke right now. Please try again later.", ephemeral=True)

    # A meme command... well, just because
    @app_commands.command(name="meme", description="Get a random SFW meme.")
    async def meme(self, interaction: discord.Interaction):
        """Sends a random meme URL."""
        logger.info(f"Meme command triggered by {interaction.user.name}")
        await interaction.response.defer()
        
        meme_url = get_meme_url()

        # Send event to theslow.net
        send_event(
            event_type="meme_command_used",
            description="A user used the /meme command.",
            payload={
                "user_id": str(interaction.user.id),  # safe to log internally
                "username": interaction.user.name,
                "guild_id": str(interaction.guild_id) if interaction.guild_id else "DM",
                "channel_id": str(interaction.channel_id),
            },
            color=0x8c00ff,
            webhook_title="A user used /meme",
            webhook_description= "Hopefully my response was appropriate. 😅"
        )
        
        if meme_url:
            await interaction.followup.send(meme_url)
        else:
            logger.error("Failed to get meme URL from service.")
            await interaction.followup.send("Sorry, the meme stash is empty right now. Please try again later.", ephemeral=True)

    # QOTD Command because everyone needs a little inspiration
    @app_commands.command(name="qotd", description="Get the quote of the day.")
    async def qotd(self, interaction: discord.Interaction):
        """Sends the quote of the day."""
        logger.info(f"QOTD command triggered by {interaction.user.name}")
        await interaction.response.defer()
        
        quote = get_qotd()

        # Send event to theslow.net
        send_event(
            event_type="qotd_command_used",
            description="A user used the /qotd command.",
            payload={
                "user_id": str(interaction.user.id),  # safe to log internally
                "username": interaction.user.name,
                "guild_id": str(interaction.guild_id) if interaction.guild_id else "DM",
                "channel_id": str(interaction.channel_id),
            },
            color=0x8c00ff,
            webhook_title="A user used /qotd",
            webhook_description= "They needed some inspiration! 💪"
        )
        
        if quote:
            await interaction.followup.send(quote)
        else:
            logger.error("Failed to get QOTD from service.")
            await interaction.followup.send("Sorry, I couldn't find the quote of the day. Please try again later.", ephemeral=True)

    # A bored command because someone needs a reminder to clean out their fridge
    @app_commands.command(name="bored", description="Get a random activity suggestion.")
    async def bored(self, interaction: discord.Interaction):
        """Suggests a random activity."""
        logger.info(f"Bored command triggered by {interaction.user.name}")
        await interaction.response.defer()
        
        activity = get_activity()

        # Send event to theslow.net
        send_event(
            event_type="bored_command_used",
            description="A user used the /bored command.",
            payload={
                "user_id": str(interaction.user.id),  # safe to log internally
                "username": interaction.user.name,
                "guild_id": str(interaction.guild_id) if interaction.guild_id else "DM",
                "channel_id": str(interaction.channel_id),
            },
            color=0x8c00ff,
            webhook_title="A user used /bored",
            webhook_description= "Hoooooly someone is bored... 🤡 "
        )
        
        if activity:
            await interaction.followup.send(f"Feeling bored? Why not try this:\n**{activity}**")
        else:
            logger.error("Failed to get activity from service.")
            await interaction.followup.send("Sorry, I'm out of ideas right now. Maybe browse Reddit?", ephemeral=True)


# setup function which loads the cog as required.
async def setup(bot: commands.Bot):
    """Adds the FunCog to the bot."""
    await bot.add_cog(FunCog(bot))
    logger.info("FunCog loaded successfully.")

