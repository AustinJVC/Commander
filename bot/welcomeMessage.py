
from discord import File
from discord.ext import commands
from dotenv import load_dotenv
from random import randrange
from easy_pil import Editor, load_image_async, Font
import io

def generate_welcome_image(profile_image, server_name, member_name):
    background_image = ["road.jpg", "sky.jpg", "skyline.jpg"]
    background_number = randrange(3)
    background = Editor("res/welcomeMessages/" + background_image[background_number])
    print("Background " + background_image[background_number] +" has been selected.")

    profile = Editor(profile_image).resize((300, 300)).circle_image()
    print("profile image resized and circled.")
    poppins = Font.poppins(size=100, variant='bold')
    print("Font declared")
    poppins_small = Font.poppins(size=60, variant='light')
    print("Small font declared.")
    background.paste(profile, (800, 200))
    background.ellipse((800, 200), 300, 300, outline='white', stroke_width=5)

    background.text((960, 600), f"Welcome to {server_name}", color='white', font=poppins, align='center')
    print("Welcome message on image declared")
    background.text((960,750), f"{member_name}", color='white', font=poppins_small, align='center')
    print("Welcome message user declared")
     # Save the image to a BytesIO object
    image_bytes_io = io.BytesIO()
    print("Set image bytes io")
    background.save(image_bytes_io, format="JPEG")
    print("saved image bytes io")
    image_bytes_io.seek(0)
    print("seeking image")

    return image_bytes_io.getvalue() 