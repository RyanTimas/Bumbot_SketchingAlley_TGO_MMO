import os
from datetime import date

import discord

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
