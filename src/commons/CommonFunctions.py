import os
from datetime import date

import discord
import io
from PIL import Image

from src.resources.constants.general_constants import IMAGE_FOLDER_PATH

#************************************************************************************
#--------------------------------FILE FUNCTIONS--------------------------------------
#************************************************************************************
"""Builds a discord.File object from an image file in the IMAGE_FOLDER_PATH directory."""
def build_image_file(image_name: str) -> discord.File:
    image_name += ".png"

    file_path = os.path.join(os.path.join(IMAGE_FOLDER_PATH, image_name))
    try:
        if not os.path.isfile(file_path):
            print(f"Image file '{file_path}' not found.")
            return None
        return discord.File(file_path, filename=image_name)
    except Exception as e:
        print(f"Error loading image file '{file_path}': {e}")
        return None


#************************************************************************************
#-------------------------------IMAGE FUNCTIONS-------------------------------------
#************************************************************************************
def to_grayscale(discord_file):
    discord_file.fp.seek(0)
    img = Image.open(discord_file.fp)
    if img.mode in ("RGBA", "LA"):
        img = img.convert("LA")  # Grayscale + alpha
    else:
        img = img.convert("L")  # Grayscale only
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return discord.File(buf, filename=discord_file.filename)