#Importing
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import logging

# Set logging directories & files. Ensure they exist, if they don't exist, create them. Set the configuration for logging.
log_directory = "logs"
log_file_path = os.path.join(log_directory, "discord_bot.log")

if not os.path.exists(log_directory):
    try:
        os.makedirs(log_directory)
    except OSError as e:
        print(f"CRITICAL: Could not create log directory '{log_directory}'. Logging disabled. Error: {e}") 
        exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)-8s] [%(name)-15s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=log_file_path,
    filemode='a',
    encoding='utf-8',
    force=True
)

logging.getLogger('discord').setLevel(logging.INFO) 
logging.getLogger('discord.http').setLevel(logging.WARNING)

logger = logging.getLogger(__name__) 

# Load environment variables for customization. 
load_dotenv()
logger.info("Loading environment variables from .env file...")

#Set the discord bot token. If there isn't a token, exit the program. 
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if DISCORD_BOT_TOKEN is None:
    logger.critical("CRITICAL: DISCORD_BOT_TOKEN not found in .env file. Bot cannot start.")
    exit(1)

# Set the discord bot status. If there isn't a status set, use the default status of "Watching you stay inside!" 
DISCORD_BOT_STATUS = os.getenv('DISCORD_BOT_STATUS', "you stay inside!")
logger.info(f"Bot status set to: '{DISCORD_BOT_STATUS}'")

# Set the weather API key. If there isn't a key, log it and move on.
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
if WEATHER_API_KEY is None:
    logger.warning("WEATHER_API_KEY not found in .env file. Weather-related commands may not function.")

# Set up the discord bot, set intents.
logger.debug("Setting up Discord intents...")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

logger.info("Initializing commands.Bot instance...")

bot = commands.Bot(command_prefix="!", intents=intents) 

# Load all cogs which are used for bot functionality.
async def load_cogs():
    cogs_path = 'cogs'
    logger.info("-" * 20)
    logger.info(f"Attempting to load cogs from directory: '{cogs_path}'...")
    loaded_cogs_count = 0
    failed_cogs_count = 0
    
    #Check if the cogs directory is there
    if not os.path.isdir(cogs_path):
        logger.warning(f"Cogs directory '{cogs_path}' not found. Skipping Cog loading.")
        return
    
    #For each cog in the directory, load it.
    for filename in os.listdir(cogs_path):
        if filename.endswith('.py') and filename != '__init__.py' and not filename.startswith(('.', '_')):
            cog_module_name = f"{cogs_path}.{filename[:-3]}" # Format like 'cogs.utility_cog'
            try:
                await bot.load_extension(cog_module_name)
                logger.info(f"  [OK] Successfully loaded cog: {cog_module_name}")
                loaded_cogs_count += 1
            except commands.ExtensionAlreadyLoaded:
                 logger.warning(f"  [!] Cog already loaded: {cog_module_name}")
            except commands.ExtensionNotFound:
                 logger.error(f"  [FAIL] Cog module not found: {cog_module_name}")
                 failed_cogs_count += 1
            except commands.NoEntryPointError:
                 logger.error(f"  [FAIL] Cog '{cog_module_name}' has no setup() function.")
                 failed_cogs_count += 1
            except commands.ExtensionFailed as e:
                 logger.error(f"  [FAIL] Cog '{cog_module_name}' setup failed: {e.original}", exc_info=True) 
                 failed_cogs_count += 1
            except Exception as e:
                logger.error(f"  [FAIL] Failed to load cog {cog_module_name}: {type(e).__name__} - {e}", exc_info=True) 
                failed_cogs_count += 1
                
    logger.info(f"Cog loading process complete. Loaded: {loaded_cogs_count}, Failed: {failed_cogs_count}")
    logger.info("-" * 20)

# The big boy himself, this is it. The big shabang! 
@bot.event
async def on_ready():
    
    # Logs the bot info, including the bot name, how many servers it's connected to, and discord version.
    logger.info("-" * 30)
    logger.info(f"Logged in as: {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guild(s).")
    logger.info(f"Using discord.py version: {discord.__version__}")
    logger.info("Bot is ready and online.")
    logger.info("-" * 30)

    # Sync commands to discord, very very important :) 
    logger.info("Attempting to sync application (slash) commands globally...")
    try:
        synced_commands = await bot.tree.sync() 
        logger.info(f"Successfully synced {len(synced_commands)} application commands globally.")
    except discord.errors.Forbidden:
         logger.error("Failed to sync commands: Bot lacks the 'applications.commands' scope.")
    except Exception as e:
        logger.error(f"Failed to sync application commands: {e}", exc_info=True) 
    
    # Change the discord status of the bot, or as the cool kids call it, "presence" 
    logger.info(f"Setting bot presence to 'Watching {DISCORD_BOT_STATUS}'...")
    try:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=str(DISCORD_BOT_STATUS)))
        logger.info("Bot presence updated successfully.")
    except Exception as e:
        logger.error(f"Failed to set bot presence: {e}", exc_info=True)

    logger.info("-" * 30)

# Our main function, some may call this the boss since all it does is delegate.
async def main():
    async with bot:
        await load_cogs() 
        
        logger.info("Attempting to connect to Discord...")
        await bot.start(DISCORD_BOT_TOKEN)

# This part is purely AI because although we aren't vibe coders, we definitely didn't wanna spend the time learning asyncio.  
if __name__ == "__main__":
    try:
        # Run the main asynchronous function
        asyncio.run(main())
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        logger.info("Received KeyboardInterrupt. Initiating shutdown...")
        # asyncio tasks are typically cancelled automatically by asyncio.run() on exit
    except discord.LoginFailure:
        # Specific error for bad tokens (already logged critical, but catch again)
        logger.critical("Login Failure: The provided DISCORD_BOT_TOKEN is invalid or expired.")
    except Exception as e:
        # Catch any other unexpected errors during startup or runtime
        # Using critical because this is an uncaught exception at the highest level
        logger.critical(f"An unexpected error occurred outside the main bot loop: {e}", exc_info=True) 
    finally:
        # This will run after the bot stops, whether normally or due to an error
        logger.info("Bot process has finished.")
        # Ensure logs are flushed before exiting (though usually handled by handlers)
        logging.shutdown() 
