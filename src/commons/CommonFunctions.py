import os
from datetime import date

import discord
import io
from PIL import Image, ImageFont, ImageDraw
from discord import File

from src.resources.constants.TGO_MMO_constants import BLACKBEAR_IMAGE_ROOT, FONT_COLOR_BLACK
from src.resources.constants.general_constants import IMAGE_FOLDER_BASE_PATH, IMAGE_FOLDER_IMAGES

#************************************************************************************
#--------------------------------FILE FUNCTIONS--------------------------------------
#************************************************************************************
"""Builds a discord.File object from an image file in the IMAGE_FOLDER_PATH directory."""
def build_image_file(image_name: str) -> discord.File:
    image_name += ".png"

    file_path = get_image_path(image_name)
    try:
        if not os.path.isfile(file_path):
            print(f"Image file '{file_path}' not found.")
            return None
        return discord.File(file_path, filename=image_name)
    except Exception as e:
        print(f"Error loading image file '{file_path}': {e}")
        return None


def get_image_path(image_name: str, folder_location: str = IMAGE_FOLDER_IMAGES) -> str:
    path = os.path.join(os.path.join(IMAGE_FOLDER_BASE_PATH, folder_location))
    return os.path.join(os.path.join(path, image_name))


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


def convert_to_png(image: Image, file_name):
     with io.BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        png_img = File(fp=image_binary, filename=file_name)
        return png_img


def add_text_to_image(image: Image.Image, font, text: str = "", position= (0,0), color: tuple = FONT_COLOR_BLACK):
    draw = ImageDraw.Draw(image)
    draw.text(position, text= text, font=font, fill=color, anchor="mm")
    return image

def center_text_on_pixel(text: str, font: ImageFont.FreeTypeFont, center_pixel_location = (0, 0)):
    text_bbox = font.getbbox(text)

    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x = center_pixel_location[0] - text_width / 2
    y = center_pixel_location[1] - text_height / 2
    return (x, y)

#************************************************************************************
#-------------------------------FONT FUNCTIONS-------------------------------------
#************************************************************************************
def load_font(font_path, font_size):
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
    return font


#************************************************************************************
#-------------------------------DISCORD FUNCTIONS------------------------------------
#************************************************************************************
def get_user_discord_profile_pic(user = None):
    avatar_url = user.display_avatar.url if hasattr(user,'display_avatar') else user.avatar.url if user.avatar else user.default_avatar.url
    return avatar_url
