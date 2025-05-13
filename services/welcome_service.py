# services/welcome_service.py
import discord
from discord import File # Explicit import is good practice
import random
import os
import logging
# Import specific components from easy_pil
from easy_pil import Editor, load_image_async, Font 
# Pillow is used internally by easy_pil, but we don't need to import it directly here

# Get a logger instance for this service file
logger = logging.getLogger(__name__)

# --- Font Configuration ---
# It's generally better to load fonts using absolute paths or paths relative 
# to the service file's location if they are bundled with the bot code.
# Assuming fonts are accessible system-wide or via path for now.
# If fonts are local, adjust the path e.g., Font("path/to/Poppins-Bold.ttf", size=100)
try:
    # Ensure you have Poppins font installed or provide direct paths
    # Example using direct path (replace with your actual path if needed):
    # poppins_bold_path = os.path.join(os.path.dirname(__file__), '..', 'res', 'fonts', 'Poppins-Bold.ttf') 
    # poppins_light_path = os.path.join(os.path.dirname(__file__), '..', 'res', 'fonts', 'Poppins-Light.ttf')
    # poppins_bold = Font(poppins_bold_path, size=100)
    # poppins_light = Font(poppins_light_path, size=60)
    
    # Using easy_pil's built-in font loading (requires font installed on system)
    poppins_bold = Font.poppins(size=100, variant='bold')
    poppins_light = Font.poppins(size=60, variant='light')
    FONTS_LOADED = True
    logger.info("Poppins fonts loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load Poppins font. Welcome images might not work correctly. Error: {e}", exc_info=True)
    # Define fallback fonts or disable the service if fonts are critical
    try:
        poppins_bold = Font.montserrat(size=100) # Example fallback
        poppins_light = Font.montserrat(size=60)
        logger.warning("Using Montserrat font as fallback.")
        FONTS_LOADED = True # Still usable with fallback
    except Exception as fallback_e:
        logger.critical(f"Fallback font Montserrat also failed to load: {fallback_e}. Disabling welcome image generation.")
        poppins_bold = None
        poppins_light = None
        FONTS_LOADED = False 

# --- Configuration ---
# Use os.path.join for better path construction, assuming 'res' is at project root
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
    if not FONTS_LOADED or not poppins_bold or not poppins_light:
        logger.error("Cannot generate welcome image: Fonts failed to load or are missing.")
        return None

    # --- Select Background ---
    if not BACKGROUND_IMAGES:
        logger.error("Cannot generate welcome image: No background images configured.")
        return None
        
    bg_path = None # Initialize bg_path
    try:
        selected_bg_name = random.choice(BACKGROUND_IMAGES)
        bg_path = os.path.join(BACKGROUND_DIR, selected_bg_name)
        
        # Check if background file exists
        if not os.path.exists(bg_path):
             logger.error(f"Background image not found at path: {bg_path}")
             return None

        # Pass the file path directly to the Editor
        background = Editor(bg_path) 
        logger.debug(f"Loaded background image: {bg_path}")

    except FileNotFoundError:
         logger.error(f"Background image file not found at expected path: {bg_path}")
         return None
    except Exception as e:
        # Catch other potential errors during background loading (e.g., PIL errors)
        logger.error(f"Failed to load background image '{bg_path}': {e}", exc_info=True)
        return None

    # --- Load and Process Profile Picture ---
    try:
        # Load profile image asynchronously from URL
        profile_image = await load_image_async(str(member_avatar_url))
        logger.debug(f"Loaded profile image for {member_name} from URL.")
        
        # Resize and make circular
        profile = Editor(profile_image).resize((300, 300)).circle_image()
        logger.debug("Resized and circled profile image.")

    except Exception as e:
        # Catch errors during avatar download or processing
        logger.error(f"Failed to load or process profile image for {member_name} from {member_avatar_url}: {e}", exc_info=True)
        return None

    # --- Composite Image ---
    try:
        # *** FIX: Access width/height via the .image attribute ***
        # Ensure both background and profile have the .image attribute accessible
        if not hasattr(background, 'image') or not hasattr(profile, 'image'):
             logger.error("Internal error: Editor object missing '.image' attribute after loading.")
             return None

        # Calculate paste coordinates using .image.width
        paste_x = (background.image.width - profile.image.width) // 2  # Center horizontally
        paste_y = 190 # Vertical position (adjust as needed)
        background.paste(profile, (paste_x, paste_y)) 
        
        # Add white circle outline around profile picture
        # Ellipse coordinates are top-left corner (same as paste) and dimensions
        background.ellipse((paste_x, paste_y), width=profile.image.width, height=profile.image.height, outline='white', stroke_width=5)
        
        # Add text elements
        # Center text horizontally using background.image.width
        text_y1 = 600 # Adjust vertical position as needed
        text_y2 = 750 # Adjust vertical position as needed
        background.text((background.image.width // 2, text_y1), f"Welcome to {server_name}", color='white', font=poppins_bold, align='center')
        background.text((background.image.width // 2, text_y2), f"{member_name}", color='white', font=poppins_light, align='center')
        logger.debug("Added text elements to the image.")

    except Exception as e:
        logger.error(f"Failed during image composition (paste/text/ellipse): {e}", exc_info=True)
        return None

    # --- Prepare and Return File ---
    try:
        # Get image bytes
        image_bytes = background.image_bytes
        # Create discord.File object
        # Use a generic filename or the background name, suggest PNG format
        output_filename = f"welcome_{member_name}.png"
        file = discord.File(fp=image_bytes, filename=output_filename) 
        logger.info(f"Successfully generated welcome image '{output_filename}' for {member_name} in {server_name}.")
        return file
    except Exception as e:
        logger.error(f"Failed to get image bytes or create discord.File: {e}", exc_info=True)
        return None
