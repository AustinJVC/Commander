from discord import File
from random import randrange, randint
from easy_pil import Editor, load_image_async, Font

poppins = Font.poppins(size=100, variant='bold')
poppins_small = Font.poppins(size=60, variant='light')

async def generate_image(member_avatar, member_name, server_name):
    """
        Takes in user info, creates a welcome message, then returns it.
        *Sends logs to console.

    Args:
        member_avatar (str): Discord user avatar URL
        member_name (str): Discord username
        server_name (str): Discord server name

    Returns:
        file: The welcome image
    """
    #Selects a background image
    background_image = ["road.jpg", "sky.jpg", "skyline.jpg"]
    background_number = randrange(3)
    background = Editor("../res/welcomeMessages/" + background_image[background_number])
    
    
    print("SELECTED BACKGROUND IMAGE")
    profile_image = await load_image_async(str(member_avatar))
    print("LOADED PROFILE IMAGE")
    profile = Editor(profile_image).resize((300, 300)).circle_image()
    print("RESIZED IMAGE")
    background.paste(profile, (800, 200))
    background.ellipse((800, 200), 300, 300, outline='white', stroke_width=5)
    background.text((960, 600), f"Welcome to {server_name}", color='white', font=poppins, align='center')
    background.text((960,750), f"{member_name}", color='white', font=poppins_small, align='center')
    print("EDITED IMAGE")
    file = File(fp=background.image_bytes, filename='road.jpg')
    print("FILE GENERATED")
    print("ATTEMPTING TO RETURN FILE")
    
    return file