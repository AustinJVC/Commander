import discord
from discord import app_commands
from discord.ext import commands
import datetime
import os
import logging
from services.send_event import send_event

#We need ordinals for logging, because "May 1st" is better than "May 1".
def get_ordinal(n):
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

# Oh my god, it's time for welcome images! But this part just tries to import the generate image function.
try:
    from services.welcome_service import generate_image 
    WELCOME_SERVICE_AVAILABLE = True
except ImportError:
    logging.warning("Could not import 'generate_image' from 'services.welcome_service'. Welcome image on join and /test_welcome will be disabled.")
    WELCOME_SERVICE_AVAILABLE = False
    async def generate_image(*args, **kwargs): return None 

#Define the logger 
logger = logging.getLogger(__name__)

#This is for SERVER logging, not PROGRAM LOGGING. don't mix those two up. This logs SERVER EVENTS in the server
class ServerEventsCog(commands.Cog, name="Server Logging"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log_channel_id = None
        self.log_channel = None

        # Get the log channel ID. If it doesn't work, continue like nothing happened.
        log_id_str = os.getenv('LOG_CHANNEL_ID')
        if log_id_str:
            try:
                self.log_channel_id = int(log_id_str)
                logger.info(f"ServerEventsCog initialized. Log Channel ID set to: {self.log_channel_id}")
            except ValueError:
                logger.error(f"Invalid LOG_CHANNEL_ID found in .env: '{log_id_str}'. Must be an integer. Server event logging disabled.")
                self.log_channel_id = None
        else:
            logger.warning("LOG_CHANNEL_ID not found in .env file. Server event logging to Discord channel is disabled.")

    #Gets the log channel based on the channel ID, then returns the discord text channel object. 
    async def _get_log_channel(self) -> discord.TextChannel | None:
        if not self.log_channel_id:
             return None

        if self.log_channel and isinstance(self.log_channel, discord.TextChannel) and self.log_channel.id == self.log_channel_id:
            return self.log_channel

        logger.debug(f"Attempting to fetch log channel with ID: {self.log_channel_id}")
        try:
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
            
    # Sends the log embed to the log channel 
    async def _send_log_embed(self, embed: discord.Embed):
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

    # This is for testing, but is a permanent command. Users can use this to preview their welcome image!
    @app_commands.command(name="test_welcome", description="Generates a test welcome image using your info.")
    async def test_welcome(self, interaction: discord.Interaction):
        logger.info(f"/test_welcome command triggered by {interaction.user} (ID: {interaction.user.id}) in server '{interaction.guild.name}'")
        await interaction.response.defer(ephemeral=True)

        if not WELCOME_SERVICE_AVAILABLE:
            logger.error("Welcome service is not available (failed import). Cannot run /test_welcome.")
            await interaction.followup.send("Sorry, the welcome image generator is currently unavailable.", ephemeral=True)
            return

        member_avatar_url = interaction.user.display_avatar.url
        member_name = interaction.user.display_name
        server_name = interaction.guild.name

        # Send event to theslow.net
        send_event(
            event_type="testwelcome_command_used",
            description="A user used the /test_welcome command.",
            payload={
                "user_id": str(interaction.user.id),  # safe to log internally
                "username": interaction.user.name,
                "guild_id": str(interaction.guild_id) if interaction.guild_id else "DM",
                "channel_id": str(interaction.channel_id),
            },
            color=0x8c00ff,
            webhook_title="A user used /test_welcome",
            webhook_description= "They didn't have enough friends to see it in action, had to test it all alone... 🕴️"
        )

        try:
            welcome_file = await generate_image(member_avatar_url, member_name, server_name)
        except Exception as e:
            logger.error(f"An unexpected error occurred calling generate_image for test: {e}", exc_info=True)
            welcome_file = None

        if welcome_file:
            logger.info(f"Successfully generated test welcome image for {interaction.user.name}.")
            await interaction.followup.send("Here is your test welcome image:", file=welcome_file, ephemeral=True)
        else:
            logger.error(f"generate_image returned None for test command user {interaction.user.name}.")
            await interaction.followup.send("Sorry, I couldn't generate the test welcome image. Please check the bot logs for errors.", ephemeral=True)


    # This listens for messages which are edits.
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # Ignore edits if they're not from users.
        if before.author.bot or before.content == after.content or not self.log_channel_id:
            return
        
        # Redundancy to ensure that the message objects are complete
        if not before.guild or not after.guild or not after.channel:
             logger.debug("Ignoring message edit event with incomplete data (likely cache).")
             return

        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        footer = f"User ID: {after.author.id} | Msg ID: {after.id} | {timestamp}"
        
        before_content = before.content[:1020] + "..." if len(before.content) > 1024 else before.content
        after_content = after.content[:1020] + "..." if len(after.content) > 1024 else after.content

        embed = discord.Embed(
            title=f"Message Edited in #{after.channel.name}", 
            description=f"[Jump to Message]({after.jump_url})",
            color=discord.Color.orange()
        )
        author_name = str(after.author)
        author_icon = after.author.display_avatar.url
        embed.set_author(name=author_name, icon_url=author_icon)
        embed.add_field(name="Before:", value=f"```{before_content}```" if before_content else "`[Empty Message]`", inline=False)
        embed.add_field(name="After:", value=f"```{after_content}```" if after_content else "`[Empty Message]`", inline=False)
        embed.set_footer(text=footer)
        
        await self._send_log_embed(embed)
        logger.debug(f"Logged message edit by {author_name} in #{after.channel.name}")


    # This listens for messages which are deleted.
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        # Ignore messages which are sent from the bot, or are embeds.
        if message.author.bot or not self.log_channel_id or message.content is None:
            return
            
        # Checks to ensure message is complete.
        if not message.guild or not message.channel:
             logger.debug("Ignoring message delete event with incomplete data (likely cache).")
             return

        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        footer = f"Author ID: {message.author.id} | Msg ID: {message.id} | {timestamp}"
        
        deleted_content = message.content[:1020] + "..." if len(message.content) > 1024 else message.content

        embed = discord.Embed(
            title=f"Message Deleted in #{message.channel.name}", 
            color=discord.Color.red()
        )
        author_name = str(message.author)
        author_icon = message.author.display_avatar.url
        embed.set_author(name=author_name, icon_url=author_icon)
        if deleted_content:
             embed.add_field(name="Deleted Message:", value=f"```{deleted_content}```", inline=False)
        else:
             embed.add_field(name="Deleted Message:", value="`[Empty or Embed Message]`", inline=False)

        if message.attachments:
            files_str = ""
            for att in message.attachments:
                line = f"- {att.filename} ({att.size // 1024} KB)\n"
                if len(files_str) + len(line) > 1020: 
                     files_str += "..."
                     break
                files_str += line
            embed.add_field(name="Attachments:", value=files_str.strip(), inline=False) 

        embed.set_footer(text=footer)
        
        await self._send_log_embed(embed)
        logger.debug(f"Logged message delete by {author_name} in #{message.channel.name}")


    # This listens for voice channel changes.
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot or not self.log_channel_id:
            return

        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        footer = f"ID: {member.id} | {timestamp}"
        author_name = str(member)
        author_icon = member.display_avatar.url
        
        embed = None

        # User joins VC, did not switch 
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="Member Joined Voice Channel", 
                description=f"{member.mention} joined **#{after.channel.name}**",
                color=discord.Color.green() # 0x56FF00
            )
        # User leaves VC 
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title="Member Left Voice Channel", 
                description=f"{member.mention} left **#{before.channel.name}**",
                color=discord.Color.red() # 0xFF0000
            )
        # User switches VC
        elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            embed = discord.Embed(
                title="Member Switched Voice Channel", 
                description=f"{member.mention} moved from **#{before.channel.name}** to **#{after.channel.name}**",
                color=discord.Color.yellow() 
            )

        if embed:
            embed.set_author(name=author_name, icon_url=author_icon)
            embed.set_footer(text=footer)
            await self._send_log_embed(embed)
            logger.debug(f"Logged voice state update for {author_name}: {embed.title}")


    # This listens for new users.
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        #Ignore is a bot joins
        if member.bot:
            return

        send_event(
            event_type="user_joined_commander_server",
            description="A user just joined the Commander userbase.",
            payload={
                "user_id": str(member.id),  # safe to log internally
                "username": member.name,
                "guild_id": str(member.guild.id) if member.guild.id else "DM",
                "member_displayname": str(member.display_name),
            },
            color=0x8c00ff,
            webhook_title="A user just joined the Commander userbase.",
            webhook_description= "Look at that, the commander user base is growing. 🌱"
        )

        #Yippeee! Image generation. Check if it's available.
        if WELCOME_SERVICE_AVAILABLE:
            system_channel = member.guild.system_channel
            if system_channel and system_channel.permissions_for(member.guild.me).send_messages:
                logger.info(f"Attempting welcome image for {member.name} in {member.guild.name}")
                try:
                    avatar_url = member.display_avatar.url 
                    welcome_file = await generate_image(avatar_url, member.name, member.guild.name) 
                    if welcome_file:
                        await system_channel.send(f"Welcome {member.mention}!", file=welcome_file)
                    else:
                         logger.warning(f"generate_image returned None for {member.name}.")
                except Exception as e:
                    logger.error(f"Failed to generate or send welcome image for {member.name}: {e}", exc_info=True)
            elif not system_channel:
                 logger.warning(f"Guild '{member.guild.name}' has no system channel set for welcome messages.")
            else:
                 logger.warning(f"Bot lacks permissions to send messages in system channel of '{member.guild.name}'.")
        
        if not self.log_channel_id:
            return

        #Get some info for the embed.
        join_position = member.guild.member_count
        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        created_at = member.created_at
        created_str = created_at.strftime(f"%B {get_ordinal(created_at.day)} %Y")
        account_age = discord.utils.utcnow() - created_at

        #Make the account age look nice
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
            description=f"{member.mention} {member.name}#{member.discriminator}",
            color=discord.Color.green()
        )
        author_name = str(member)
        author_icon = member.display_avatar.url
        embed.add_field(name="Account Details", value=f"Created: {created_str}\nAge: ~{age_str}", inline=True)
        embed.add_field(name="Member Count", value=f"{member.guild.member_count}", inline=True)
        embed.set_thumbnail(url=author_icon)
        embed.set_footer(text=footer)
        
        await self._send_log_embed(embed)
        logger.info(f"Logged member join: {author_name} to {member.guild.name}")


    # This listens for users leaving.
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.bot or not self.log_channel_id:
            return

        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        # Calculate time spent in server
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
             joined_str = "Unknown"

        footer = f"ID: {member.id} | {timestamp}"

        embed = discord.Embed(
            title="Member Left", 
            description=f"{member.mention} {member.name}#{member.discriminator}",
            color=discord.Color.dark_red()
        )
        author_name = str(member)
        author_icon = member.display_avatar.url
        embed.add_field(name="Joined On", value=f"{joined_str}{time_spent_str}", inline=False)
        embed.set_thumbnail(url=author_icon)
        embed.set_footer(text=footer)
        
        send_event(
            event_type="user_left_commander_server",
            description="A user just left the Commander userbase.",
            payload={
                "user_id": str(member.id),  # safe to log internally
                "username": member.name,
                "guild_id": str(member.guild.id) if member.guild.id else "DM",
                "member_displayname": str(member.display_name),
            },
            color=0x8c00ff,
            webhook_title="A user just left the Commander userbase.",
            webhook_description= "Look at that, the commander user base is... dying 🥀"
        )

        await self._send_log_embed(embed)
        logger.info(f"Logged member leave: {author_name} from {member.guild.name}")


    # This listens for user updates such as name, avatar, etc.
    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if before.bot or not self.log_channel_id:
            return

        timestamp = discord.utils.utcnow().strftime(f"%A, %B {get_ordinal(discord.utils.utcnow().day)} %Y, at %I:%M %p UTC")
        footer = f"ID: {after.id} | {timestamp}"
        
        embed = None

        # check changed
        if before.name != after.name:
            embed = discord.Embed(title="Username Changed", color=discord.Color.purple())
            embed.set_author(name=str(after), icon_url=after.display_avatar.url)
            embed.add_field(name="Before:", value=f"`{before.name}`", inline=False)
            embed.add_field(name="After:", value=f"`{after.name}`", inline=False)
            embed.set_thumbnail(url=before.display_avatar.url)

        elif before.discriminator != after.discriminator and after.discriminator != "0":
             embed = discord.Embed(title="Username/Discriminator Changed", color=discord.Color.purple())
             embed.set_author(name=str(after), icon_url=after.display_avatar.url)
             embed.add_field(name="Before:", value=f"`{str(before)}`", inline=False)
             embed.add_field(name="After:", value=f"`{str(after)}`", inline=False)
             embed.set_thumbnail(url=after.display_avatar.url)

        elif before.display_avatar != after.display_avatar:
            embed = discord.Embed(title="Avatar Changed", color=discord.Color.purple())
            embed.set_author(name=str(after), icon_url=before.display_avatar.url)
            embed.set_thumbnail(url=after.display_avatar.url)

        if embed:
            embed.set_footer(text=footer)
            await self._send_log_embed(embed)
            logger.debug(f"Logged user update for {str(after)}: {embed.title}")


# Setup the cog
async def setup(bot: commands.Bot):
    await bot.add_cog(ServerEventsCog(bot))
    logger.info("Cog 'ServerEventsCog' loaded successfully.")
