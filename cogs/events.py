# cogs/server_events_cog.py
import discord
from discord import app_commands # Import app_commands for slash commands
from discord.ext import commands
import datetime
import os
import logging

# --- Helper Function (Copied from ordinal.py) ---
# Move this to a utils file if preferred
def get_ordinal(n):
    """Converts an integer to its ordinal representation (e.g., 1 -> 1st, 2 -> 2nd)."""
    # Check if n is an integer or can be converted
    if not isinstance(n, int):
        try:
            n = int(n)
        except (ValueError, TypeError):
            return str(n) # Return original if not convertible to int

    if 10 <= n % 100 <= 13:
        return str(n) + "th"
    last_digit = n % 10
    if last_digit == 1:
        return str(n) + "st"
    elif last_digit == 2:
        return str(n) + "nd"
    elif last_digit == 3:
        return str(n) + "rd"
    else:
        return str(n) + "th"

# --- Welcome Image Service Import (Adjust Path if Needed) ---
try:
    # Assuming you moved welcomeImage logic to a service
    from services.welcome_service import generate_image 
    WELCOME_SERVICE_AVAILABLE = True
except ImportError:
    logging.warning("Could not import 'generate_image' from 'services.welcome_service'. Welcome image on join and /test_welcome will be disabled.")
    WELCOME_SERVICE_AVAILABLE = False
    # Define a placeholder if needed, though the code below checks the flag
    async def generate_image(*args, **kwargs): return None 

# Get a logger instance for this Cog file
logger = logging.getLogger(__name__)

class ServerEventsCog(commands.Cog, name="Server Logging"):
    """
    Handles logging of server events (message edits, joins, etc.) 
    to a designated Discord channel and provides related test commands.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log_channel_id = None # Initialize to None
        self.log_channel = None    # Cache the channel object

        log_id_str = os.getenv('LOG_CHANNEL_ID')
        if log_id_str:
            try:
                self.log_channel_id = int(log_id_str)
                logger.info(f"ServerEventsCog initialized. Log Channel ID set to: {self.log_channel_id}")
                # Try to fetch the channel on init, but don't block startup
                # self.log_channel = self.bot.get_channel(self.log_channel_id) # Might be None if bot not ready
            except ValueError:
                logger.error(f"Invalid LOG_CHANNEL_ID found in .env: '{log_id_str}'. Must be an integer. Server event logging disabled.")
                self.log_channel_id = None # Explicitly disable if invalid
        else:
            logger.warning("LOG_CHANNEL_ID not found in .env file. Server event logging to Discord channel is disabled.")

    async def _get_log_channel(self) -> discord.TextChannel | None:
        """Helper to get the log channel object, fetching if needed."""
        if not self.log_channel_id:
             # Logged on init, no need to repeat unless debugging
             # logger.debug("Log channel ID not set, cannot get channel.")
             return None
        
        # Use cached channel if available and seems valid
        # Check type just in case it was somehow set incorrectly
        if self.log_channel and isinstance(self.log_channel, discord.TextChannel) and self.log_channel.id == self.log_channel_id:
            return self.log_channel

        # Fetch the channel if not cached or ID changed (unlikely)
        logger.debug(f"Attempting to fetch log channel with ID: {self.log_channel_id}")
        try:
            # Use fetch_channel as get_channel might return None if not in cache
            channel = await self.bot.fetch_channel(self.log_channel_id)
            if isinstance(channel, discord.TextChannel):
                self.log_channel = channel # Cache the fetched channel
                logger.info(f"Successfully fetched log channel: {channel.name} (ID: {channel.id})")
                return self.log_channel
            else:
                logger.warning(f"Fetched channel for ID {self.log_channel_id} is not a TextChannel (Type: {type(channel)}). Logging disabled.")
                self.log_channel_id = None # Disable if wrong type
                return None
        except discord.NotFound:
            logger.error(f"Log channel with ID {self.log_channel_id} not found by the bot.")
            self.log_channel_id = None # Disable if not found
            return None
        except discord.Forbidden:
            logger.error(f"Bot lacks permissions to fetch log channel ID {self.log_channel_id}.")
            self.log_channel_id = None # Disable if forbidden
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred fetching log channel ID {self.log_channel_id}: {e}", exc_info=True)
            return None
            
    async def _send_log_embed(self, embed: discord.Embed):
        """Sends the embed to the configured log channel."""
        log_channel = await self._get_log_channel()
        if log_channel:
            try:
                await log_channel.send(embed=embed)
            except discord.Forbidden:
                logger.error(f"Bot lacks permissions to send messages in log channel: {log_channel.name} (ID: {log_channel.id})")
            except discord.HTTPException as e:
                logger.error(f"Failed to send log message to {log_channel.name}: {e}", exc_info=True)
            except Exception as e:
                 logger.error(f"An unexpected error occurred sending log to {log_channel.name}: {e}", exc_info=True)
        # else: (No need to log here, _get_log_channel already logs issues)
        #     logger.debug("Log channel not available, skipping embed send.")

    # <<< NEW TEST COMMAND ADDED HERE >>>
    @app_commands.command(name="test_welcome", description="Generates a test welcome image using your info.")
    async def test_welcome(self, interaction: discord.Interaction):
        """Generates and sends a test welcome image for the invoking user."""
        logger.info(f"/test_welcome command triggered by {interaction.user} (ID: {interaction.user.id}) in server '{interaction.guild.name}'")
        await interaction.response.defer(ephemeral=True) # Defer and make response visible only to user

        if not WELCOME_SERVICE_AVAILABLE:
            logger.error("Welcome service is not available (failed import). Cannot run /test_welcome.")
            await interaction.followup.send("Sorry, the welcome image generator is currently unavailable.", ephemeral=True)
            return

        # Get necessary info from the interaction user
        member_avatar_url = interaction.user.display_avatar.url
        member_name = interaction.user.display_name # Use display_name for server nickname preference
        server_name = interaction.guild.name

        # Call the service function
        try:
            welcome_file = await generate_image(member_avatar_url, member_name, server_name)
        except Exception as e:
            logger.error(f"An unexpected error occurred calling generate_image for test: {e}", exc_info=True)
            welcome_file = None

        # Send the result
        if welcome_file:
            logger.info(f"Successfully generated test welcome image for {interaction.user.name}.")
            await interaction.followup.send("Here is your test welcome image:", file=welcome_file, ephemeral=True)
        else:
            logger.error(f"generate_image returned None for test command user {interaction.user.name}.")
            await interaction.followup.send("Sorry, I couldn't generate the test welcome image. Please check the bot logs for errors.", ephemeral=True)


    # --- Listener for Message Edits ---
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # Ignore edits from bots or if content hasn't changed
        if before.author.bot or before.content == after.content or not self.log_channel_id:
            return
        
        # Ensure message objects have necessary data (might be from cache)
        if not before.guild or not after.guild or not after.channel:
             logger.debug("Ignoring message edit event with incomplete data (likely cache).")
             return

        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        footer = f"User ID: {after.author.id} | Msg ID: {after.id} | {timestamp}"
        
        # Limit content length for embeds
        before_content = before.content[:1020] + "..." if len(before.content) > 1024 else before.content
        after_content = after.content[:1020] + "..." if len(after.content) > 1024 else after.content

        embed = discord.Embed(
            title=f"Message Edited in #{after.channel.name}", 
            description=f"[Jump to Message]({after.jump_url})", # Add jump link
            color=discord.Color.orange() # 0xFFBF00
        )
        author_name = str(after.author) # Use str() for safety
        author_icon = after.author.display_avatar.url # Use display_avatar
        embed.set_author(name=author_name, icon_url=author_icon)
        embed.add_field(name="Before:", value=f"```{before_content}```" if before_content else "`[Empty Message]`", inline=False)
        embed.add_field(name="After:", value=f"```{after_content}```" if after_content else "`[Empty Message]`", inline=False)
        embed.set_footer(text=footer)
        
        await self._send_log_embed(embed)
        logger.debug(f"Logged message edit by {author_name} in #{after.channel.name}")


    # --- Listener for Message Deletions ---
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        # Ignore deletions from bots or if channel ID isn't set
        # Also ignore if message content is None (might be old message or embed only)
        if message.author.bot or not self.log_channel_id or message.content is None:
            return
            
        # Message might be from cache and lack guild info
        if not message.guild or not message.channel:
             logger.debug("Ignoring message delete event with incomplete data (likely cache).")
             return

        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        footer = f"Author ID: {message.author.id} | Msg ID: {message.id} | {timestamp}"
        
        # Limit content length
        deleted_content = message.content[:1020] + "..." if len(message.content) > 1024 else message.content

        embed = discord.Embed(
            title=f"Message Deleted in #{message.channel.name}", 
            color=discord.Color.red() # 0xFF0000
        )
        author_name = str(message.author)
        author_icon = message.author.display_avatar.url
        embed.set_author(name=author_name, icon_url=author_icon)
        # Only add content field if it's not empty after potential truncation
        if deleted_content:
             embed.add_field(name="Deleted Message:", value=f"```{deleted_content}```", inline=False)
        else:
             embed.add_field(name="Deleted Message:", value="`[Empty or Embed Message]`", inline=False)

        
        # Add attachment info if present
        if message.attachments:
            # Format file info, limiting the total length
            files_str = ""
            for att in message.attachments:
                line = f"- {att.filename} ({att.size // 1024} KB)\n"
                if len(files_str) + len(line) > 1020: # Keep under embed field limit
                     files_str += "..."
                     break
                files_str += line
            embed.add_field(name="Attachments:", value=files_str.strip(), inline=False) 

        embed.set_footer(text=footer)
        
        await self._send_log_embed(embed)
        logger.debug(f"Logged message delete by {author_name} in #{message.channel.name}")


    # --- Listener for Voice State Updates ---
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot or not self.log_channel_id:
            return

        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        footer = f"ID: {member.id} | {timestamp}"
        author_name = str(member)
        author_icon = member.display_avatar.url
        
        embed = None # Initialize embed to None

        # Member Joins VC (was not in a channel before)
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="Member Joined Voice Channel", 
                description=f"{member.mention} joined **#{after.channel.name}**",
                color=discord.Color.green() # 0x56FF00
            )
        # Member Leaves VC (was in a channel before, isn't now)
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title="Member Left Voice Channel", 
                description=f"{member.mention} left **#{before.channel.name}**",
                color=discord.Color.red() # 0xFF0000
            )
        # Member Switches VC (channels are different and not None)
        elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            embed = discord.Embed(
                title="Member Switched Voice Channel", 
                description=f"{member.mention} moved from **#{before.channel.name}** to **#{after.channel.name}**",
                color=discord.Color.blue() # 0xFFBF00 was orange, using blue
            )
            
        # Add mute/deafen status changes if needed (can get noisy)
        # elif before.self_mute != after.self_mute: ...
        # elif before.self_deaf != after.self_deaf: ...

        if embed: # Only send if one of the conditions above was met
            embed.set_author(name=author_name, icon_url=author_icon)
            embed.set_footer(text=footer)
            await self._send_log_embed(embed)
            logger.debug(f"Logged voice state update for {author_name}: {embed.title}")


    # --- Listener for Member Joins ---
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot: # Usually ignore bot joins
            return

        # --- Send Welcome Message to System Channel (Original Logic) ---
        # Check if welcome image generation is available and desired
        if WELCOME_SERVICE_AVAILABLE:
            system_channel = member.guild.system_channel # Channel designated by Discord for welcome messages
            if system_channel and system_channel.permissions_for(member.guild.me).send_messages:
                logger.info(f"Attempting welcome image for {member.name} in {member.guild.name}")
                try:
                    # Ensure avatar URL is fetched correctly
                    avatar_url = member.display_avatar.url 
                    # Call the image generation service
                    welcome_file = await generate_image(avatar_url, member.name, member.guild.name) 
                    if welcome_file:
                        await system_channel.send(f"Welcome {member.mention}!", file=welcome_file)
                    else:
                         logger.warning(f"generate_image returned None for {member.name}.")
                         # Optionally send a text-only welcome
                         # await system_channel.send(f"Welcome {member.mention}!")
                except Exception as e:
                    logger.error(f"Failed to generate or send welcome image for {member.name}: {e}", exc_info=True)
            elif not system_channel:
                 logger.warning(f"Guild '{member.guild.name}' has no system channel set for welcome messages.")
            else:
                 logger.warning(f"Bot lacks permissions to send messages in system channel of '{member.guild.name}'.")
        
        # --- Send Log Message to Log Channel ---
        if not self.log_channel_id:
            return # Don't proceed if logging is disabled

        join_position = member.guild.member_count # member_count updates after join
        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        created_at = member.created_at # Get creation timestamp
        created_str = created_at.strftime(f"%B {get_ordinal(created_at.day)} %Y")
        # Calculate account age (optional but nice)
        account_age = discord.utils.utcnow() - created_at
        # Format age string more robustly
        if account_age.days > 1:
             age_str = f"{account_age.days} days"
        elif account_age.days == 1:
             age_str = "1 day"
        elif account_age.total_seconds() >= 3600: # More than 1 hour
             age_str = f"{int(account_age.total_seconds() // 3600)} hours"
        elif account_age.total_seconds() >= 60: # More than 1 minute
             age_str = f"{int(account_age.total_seconds() // 60)} minutes"
        else:
             age_str = f"{int(account_age.total_seconds())} seconds"


        footer = f"ID: {member.id} | {timestamp}"

        embed = discord.Embed(
            title="Member Joined", 
            description=f"{member.mention} {member.name}#{member.discriminator}", # Use mention and full tag
            color=discord.Color.green() # 0x56FF00
        )
        author_name = str(member)
        author_icon = member.display_avatar.url
        # embed.set_author(name=author_name, icon_url=author_icon) # Redundant with description/thumbnail
        embed.add_field(name="Account Details", value=f"Created: {created_str}\nAge: ~{age_str}", inline=True)
        embed.add_field(name="Member Count", value=f"{member.guild.member_count}", inline=True)
        embed.set_thumbnail(url=author_icon) # Show avatar larger
        embed.set_footer(text=footer)
        
        await self._send_log_embed(embed)
        logger.info(f"Logged member join: {author_name} to {member.guild.name}")


    # --- Listener for Member Leaves ---
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.bot or not self.log_channel_id:
            return

        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        # Calculate time spent in server (optional)
        time_spent_str = ""
        if member.joined_at:
             time_spent = discord.utils.utcnow() - member.joined_at
             if time_spent.days > 1:
                 time_spent_str = f"\nDuration: {time_spent.days} days"
             elif time_spent.days == 1:
                  time_spent_str = "\nDuration: 1 day"
             elif time_spent.total_seconds() >= 3600:
                  time_spent_str = f"\nDuration: {int(time_spent.total_seconds() // 3600)} hours"
             else:
                  time_spent_str = f"\nDuration: {int(time_spent.total_seconds() // 60)} minutes"
             joined_str = member.joined_at.strftime(f"%B {get_ordinal(member.joined_at.day)} %Y")
        else:
             joined_str = "Unknown" # Member might be from cache without join date

        footer = f"ID: {member.id} | {timestamp}"

        embed = discord.Embed(
            title="Member Left", 
            description=f"{member.mention} {member.name}#{member.discriminator}",
            color=discord.Color.dark_red() # 0xff0000
        )
        author_name = str(member)
        author_icon = member.display_avatar.url
        # embed.set_author(name=author_name, icon_url=author_icon)
        embed.add_field(name="Joined On", value=f"{joined_str}{time_spent_str}", inline=False)
        embed.set_thumbnail(url=author_icon)
        embed.set_footer(text=footer)
        
        await self._send_log_embed(embed)
        logger.info(f"Logged member leave: {author_name} from {member.guild.name}")


    # --- Listener for User Updates (Username, Avatar, etc.) ---
    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if before.bot or not self.log_channel_id:
            return

        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        footer = f"ID: {after.id} | {timestamp}"
        
        embed = None # Initialize

        # Check for specific changes
        if before.name != after.name:
            embed = discord.Embed(title="Username Changed", color=discord.Color.purple()) # 0xFF00EF
            embed.set_author(name=str(after), icon_url=after.display_avatar.url)
            embed.add_field(name="Before:", value=f"`{before.name}`", inline=False)
            embed.add_field(name="After:", value=f"`{after.name}`", inline=False)
            embed.set_thumbnail(url=before.display_avatar.url) # Show old avatar as thumb

        elif before.discriminator != after.discriminator and after.discriminator != "0": # If user migrates from discriminators or changes pomelo username
             embed = discord.Embed(title="Username/Discriminator Changed", color=discord.Color.purple())
             embed.set_author(name=str(after), icon_url=after.display_avatar.url)
             embed.add_field(name="Before:", value=f"`{str(before)}`", inline=False) # Show full old tag
             embed.add_field(name="After:", value=f"`{str(after)}`", inline=False) # Show full new tag
             embed.set_thumbnail(url=after.display_avatar.url)

        elif before.display_avatar != after.display_avatar:
            embed = discord.Embed(title="Avatar Changed", color=discord.Color.purple())
            embed.set_author(name=str(after), icon_url=before.display_avatar.url) # Show old avatar with name
            embed.set_thumbnail(url=after.display_avatar.url) # Show new avatar as thumb
        
        # Add checks for global_name if needed (less common now)
        # elif before.global_name != after.global_name: ...

        if embed:
            embed.set_footer(text=footer)
            await self._send_log_embed(embed)
            logger.debug(f"Logged user update for {str(after)}: {embed.title}")


# --- Setup Function for the Cog ---
async def setup(bot: commands.Bot):
    """Adds the ServerEventsCog to the bot."""
    # Ensure the welcome service is checked before adding the cog if it's critical
    # if not WELCOME_SERVICE_AVAILABLE:
    #     logger.critical("Welcome service not available, ServerEventsCog will not be loaded.")
    #     return # Prevent loading if welcome service is essential

    await bot.add_cog(ServerEventsCog(bot))
    # Log successful loading of the Cog using the standard logger
    logger.info("Cog 'ServerEventsCog' loaded successfully.")
