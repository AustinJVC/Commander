
from discord import File
from discord.ext import commands
from dotenv import load_dotenv
from random import randrange
from easy_pil import Editor, load_image_async, Font

def generate_welcome_image(profile_image, server_name, member_name):
    background_image = ["road.jpg", "sky.jpg", "skyline.jpg"]
    background_number = randrange(3)
    background = Editor("res/welcomeMessages/" + background_image[background_number])
    

    profile = Editor(profile_image).resize((300, 300)).circle_image()

    poppins = Font.poppins(size=100, variant='bold')

    poppins_small = Font.poppins(size=60, variant='light')

    background.paste(profile, (800, 200))
    background.ellipse((800, 200), 300, 300, outline='white', stroke_width=5)

    background.text((960, 600), f"Welcome to {server_name}", color='white', font=poppins, align='center')

    background.text((960,750), f"{member_name}", color='white', font=poppins_small, align='center')

    file = File(fp=background.image_bytes, filename='road.jpg')
    print("file generated")
    return file