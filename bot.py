# External Imports
import discord
# from discord import app_commands # Not strictly needed if all commands are in Cogs
from discord.ext import commands
# import datetime # Not used directly here anymore
from dotenv import load_dotenv
import os
import asyncio
import logging # Import logging module
# No longer need logging.handlers or sys

# --- Simplified Logging Setup (File Only) ---
# Configure logging to output INFO level messages and higher directly to a file.
# This is called ONCE when the script starts.
log_directory = "logs"
log_file_path = os.path.join(log_directory, "discord_bot.log")

# Ensure the log directory exists
if not os.path.exists(log_directory):
    try:
        os.makedirs(log_directory)
    except OSError as e:
        # Use print for critical setup errors before logging is fully configured
        print(f"CRITICAL: Could not create log directory '{log_directory}'. Logging disabled. Error: {e}", file=sys.stderr) 
        # Exit or disable logging features if the directory is essential
        exit(1) 

logging.basicConfig(
    level=logging.INFO,  # Set the minimum level to log (INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s [%(levelname)-8s] [%(name)-15s]: %(message)s', # Log message format
    datefmt='%Y-%m-%d %H:%M:%S', # Timestamp format
    filename=log_file_path, # <<< Direct logs to this file
    filemode='a', # 'a' for append (default), 'w' for overwrite each time
    encoding='utf-8', # Explicitly set encoding
    force=True # Use force=True to allow reconfiguration if basicConfig was called before (e.g., by a library)
)

# --- Optional: Set discord.py's internal logger level ---
# If you want discord.py logs in the file, ensure its level is >= INFO
# If you want FEWER discord.py logs, set its level higher (e.g., WARNING)
logging.getLogger('discord').setLevel(logging.INFO) 
logging.getLogger('discord.http').setLevel(logging.WARNING)

# --- Get a logger instance for THIS file (bot.py) ---
# Best practice: use __name__ for the logger name (will be '__main__' when run directly)
logger = logging.getLogger(__name__) 

# --- Load Environment Variables ---
load_dotenv()
logger.info("Loading environment variables from .env file...") # This will go to the file

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if DISCORD_BOT_TOKEN is None:
    # Use CRITICAL for errors that prevent the bot from starting
    logger.critical("CRITICAL: DISCORD_BOT_TOKEN not found in .env file. Bot cannot start.")
    exit(1) # Exit if the token is missing

DISCORD_BOT_STATUS = os.getenv('DISCORD_BOT_STATUS', "Watching things!") # Provide a default status
logger.info(f"Bot status set to: '{DISCORD_BOT_STATUS}'")

# --- API Key Checks (Example) ---
# Log warnings for potentially missing optional keys needed by Cogs
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
if WEATHER_API_KEY is None:
    # This is just an informational warning here; the Cog using it should handle the absence properly.
    logger.warning("WEATHER_API_KEY not found in .env file. Weather-related commands may not function.")
# Add similar checks/warnings for other optional API keys if needed

# Note: LOG_CHANNEL_ID is intentionally NOT checked/logged here, 
# as it's for server activity logging, presumably handled within a specific Cog/event listener.

# --- Bot Initialization ---
logger.debug("Setting up Discord intents...") # DEBUG messages won't show with level=INFO
intents = discord.Intents.default()
intents.message_content = True # Required for message content related events (if any)
intents.members = True         # Required for member join/update events (if any)
intents.voice_states = True    # Required for voice state events (if any)

logger.info("Initializing commands.Bot instance...") # INFO messages will show
# Using commands.Bot allows for Cogs and potentially prefix commands (though focusing on slash)
bot = commands.Bot(command_prefix="!", intents=intents) 

# --- Cog Loading ---
async def load_cogs():
    """Finds and loads all Python files as cogs from the 'cogs' directory."""
    cogs_path = 'cogs'
    logger.info("-" * 20)
    logger.info(f"Attempting to load cogs from directory: '{cogs_path}'...")
    loaded_cogs_count = 0
    failed_cogs_count = 0
    
    if not os.path.isdir(cogs_path):
        logger.warning(f"Cogs directory '{cogs_path}' not found. Skipping Cog loading.")
        return

    for filename in os.listdir(cogs_path):
        # Standard check: Python file, not __init__, not hidden/temporary
        if filename.endswith('.py') and filename != '__init__.py' and not filename.startswith(('.', '_')):
            cog_module_name = f"{cogs_path}.{filename[:-3]}" # Format like 'cogs.utility_cog'
            try:
                # The core command to load an extension (Cog)
                await bot.load_extension(cog_module_name)
                logger.info(f"  [OK] Successfully loaded cog: {cog_module_name}")
                loaded_cogs_count += 1
            except commands.ExtensionAlreadyLoaded:
                 logger.warning(f"  [!] Cog already loaded: {cog_module_name}") # Should be rare if loaded once
            except commands.ExtensionNotFound:
                 logger.error(f"  [FAIL] Cog module not found: {cog_module_name}")
                 failed_cogs_count += 1
            except commands.NoEntryPointError:
                 logger.error(f"  [FAIL] Cog '{cog_module_name}' has no setup() function.")
                 failed_cogs_count += 1
            except commands.ExtensionFailed as e:
                 # Log the original error that occurred within the Cog's setup
                 logger.error(f"  [FAIL] Cog '{cog_module_name}' setup failed: {e.original}", exc_info=True) 
                 failed_cogs_count += 1
            except Exception as e:
                # Catch any other unexpected errors during loading
                logger.error(f"  [FAIL] Failed to load cog {cog_module_name}: {type(e).__name__} - {e}", exc_info=True) 
                failed_cogs_count += 1
                
    logger.info(f"Cog loading process complete. Loaded: {loaded_cogs_count}, Failed: {failed_cogs_count}")
    logger.info("-" * 20)

# --- Bot Events ---
@bot.event
async def on_ready():
    """
    Called once the bot is fully connected and ready. 
    Syncs application commands and sets the bot's presence.
    """
    logger.info("-" * 30)
    logger.info(f"Logged in as: {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guild(s).")
    logger.info(f"Using discord.py version: {discord.__version__}")
    logger.info("Bot is ready and online.")
    logger.info("-" * 30)

    # --- Sync Application Commands ---
    logger.info("Attempting to sync application (slash) commands globally...")
    try:
        # Sync commands registered via Cogs or directly in bot.py
        synced_commands = await bot.tree.sync() 
        logger.info(f"Successfully synced {len(synced_commands)} application commands globally.")
    except discord.errors.Forbidden:
         logger.error("Failed to sync commands: Bot lacks the 'applications.commands' scope.")
    except Exception as e:
        logger.error(f"Failed to sync application commands: {e}", exc_info=True) 
    
    # --- Set Bot Presence ---
    logger.info(f"Setting bot presence to 'Watching {DISCORD_BOT_STATUS}'...")
    try:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=str(DISCORD_BOT_STATUS)))
        logger.info("Bot presence updated successfully.")
    except Exception as e:
        logger.error(f"Failed to set bot presence: {e}", exc_info=True)

    logger.info("-" * 30)
    
# --- Event Listeners for Server Activity (Example - Move to Cog) ---
# These should ideally be in their own Cog (e.g., 'cogs/server_events_cog.py')
# and use the LOG_CHANNEL_ID for sending messages to Discord, NOT the standard logger.

# --- Main Execution Block ---
async def main():
    """Main asynchronous function to load cogs and start the bot."""
    # Use bot as an async context manager for proper setup/teardown
    async with bot:
        # Load all extensions (Cogs) before starting the connection
        await load_cogs() 
        
        logger.info("Attempting to connect to Discord...")
        # Start the bot's connection to Discord using the token
        await bot.start(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    # This block runs when the script is executed directly
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
