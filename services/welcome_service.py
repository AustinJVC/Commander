import discord
from discord import File
import random
import os
import logging

from easy_pil import Editor, load_image_async, Font 

logger = logging.getLogger(__name__)

# Attempt to load the fonts
try:
    poppins_bold = Font.poppins(size=100, variant='bold')
    poppins_light = Font.poppins(size=60, variant='light')
    FONTS_LOADED = True
    logger.info("Poppins fonts loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load Poppins font. Welcome images might not work correctly. Error: {e}", exc_info=True)
    try:
        poppins_bold = Font.montserrat(size=100)
        poppins_light = Font.montserrat(size=60)
        logger.warning("Using Montserrat font as fallback.")
        FONTS_LOADED = True
    except Exception as fallback_e:
        logger.critical(f"Fallback font Montserrat also failed to load: {fallback_e}. Disabling welcome image generation.")
        poppins_bold = None
        poppins_light = None
        FONTS_LOADED = False 

#configure our background images stuff as variables
BACKGROUND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res', 'welcomeMessages'))
BACKGROUND_IMAGES = ["road.jpg", "sky.jpg", "skyline.jpg"] # Image filenames within BACKGROUND_DIR

async def generate_image(member_avatar_url: str, member_name: str, server_name: str) -> discord.File | None:
    """
    Generates a welcome image with the user's avatar and server name.

    Args:
        member_avatar_url (str): URL of the member's avatar.
        member_name (str): Name of the member.
        server_name (str): Name of the server.

    Returns:
        discord.File | None: A discord.File object containing the image bytes, 
                             or None if an error occurred.
    """
    #Do some checks to make sure that we didn't mess up somewhere along the way
    if not FONTS_LOADED or not poppins_bold or not poppins_light:
        logger.error("Cannot generate welcome image: Fonts failed to load or are missing.")
        return None

    if not BACKGROUND_IMAGES:
        logger.error("Cannot generate welcome image: No background images configured.")
        return None

    #Select a background image for our beautifully made welcome image. 
    bg_path = None
    try:
        selected_bg_name = random.choice(BACKGROUND_IMAGES)
        bg_path = os.path.join(BACKGROUND_DIR, selected_bg_name)
        
        if not os.path.exists(bg_path):
             logger.error(f"Background image not found at path: {bg_path}")
             return None
        background = Editor(bg_path) 
        logger.debug(f"Loaded background image: {bg_path}")

    except FileNotFoundError:
         logger.error(f"Background image file not found at expected path: {bg_path}")
         return None
    except Exception as e:
        # Catch other potential errors during background loading (e.g., PIL errors)
        logger.error(f"Failed to load background image '{bg_path}': {e}", exc_info=True)
        return None

    # Get the profile image, then format it
    try:
        profile_image = await load_image_async(str(member_avatar_url))
        logger.debug(f"Loaded profile image for {member_name} from URL.")
        
        profile = Editor(profile_image).resize((300, 300)).circle_image()
        logger.debug("Resized and circled profile image.")

    except Exception as e:
        logger.error(f"Failed to load or process profile image for {member_name} from {member_avatar_url}: {e}", exc_info=True)
        return None

    # Create the masterpiece which combines the profile image, server name, user name, and background image.
    try:
        if not hasattr(background, 'image') or not hasattr(profile, 'image'):
             logger.error("Internal error: Editor object missing '.image' attribute after loading.")
             return None

        # This centers the image.
        paste_x = (background.image.width - profile.image.width) // 2
        paste_y = 190
        background.paste(profile, (paste_x, paste_y)) 
        
        # This does the white circle outline around profile picture
        background.ellipse((paste_x, paste_y), width=profile.image.width, height=profile.image.height, outline='white', stroke_width=5)
        
        # Add some text for goodness sake
        text_y1 = 600
        text_y2 = 750
        background.text((background.image.width // 2, text_y1), f"Welcome to {server_name}", color='white', font=poppins_bold, align='center')
        background.text((background.image.width // 2, text_y2), f"{member_name}", color='white', font=poppins_light, align='center')
        logger.debug("Added text elements to the image.")

    except Exception as e:
        logger.error(f"Failed during image composition (paste/text/ellipse): {e}", exc_info=True)
        return None

    # Return our beautifully made welcome image
    try:
        image_bytes = background.image_bytes
        output_filename = f"welcome_{member_name}.png"
        file = discord.File(fp=image_bytes, filename=output_filename) 
        logger.info(f"Successfully generated welcome image '{output_filename}' for {member_name} in {server_name}.")
        return file
    except Exception as e:
        logger.error(f"Failed to get image bytes or create discord.File: {e}", exc_info=True)
        return None
