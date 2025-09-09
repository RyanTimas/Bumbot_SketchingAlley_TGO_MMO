import asyncio
import functools
import os
from datetime import date

import aiohttp
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


def resize_text_to_fit(text, draw, font, max_width, min_font_size=10):
        current_font = font
        current_font_size = font.size

        current_text = text

        # Check if the text already fits
        text_width = draw.textlength(text, font=current_font)

        if text_width <= max_width:
            return current_font

        # If text doesn't fit, try reducing font size
        while text_width > max_width and current_font_size > min_font_size:
            current_font_size -= 1

            # Create a new font with smaller size
            try:
                current_font = ImageFont.truetype(font.path, current_font_size)
            except IOError:
                current_font = ImageFont.load_default()

            text_width = draw.textlength(text, font=current_font)

        # If reducing font size didn't work or wasn't possible, truncate the text
        if text_width > max_width:
            # Truncate text with ellipsis
            ellipsis = "..."
            truncated_text = text

            while draw.textlength(truncated_text + ellipsis, font=font) > max_width and len(truncated_text) > 0:
                truncated_text = truncated_text[:-1]

            current_text = truncated_text + ellipsis if truncated_text else ellipsis

        return current_font



#************************************************************************************
#-------------------------------DISCORD FUNCTIONS------------------------------------
#************************************************************************************
def get_user_discord_profile_pic(user = None):
    avatar_url = user.display_avatar.url if hasattr(user,'display_avatar') else user.avatar.url if user.avatar else user.default_avatar.url
    return avatar_url


#*********************
# DISCORD VIEW HELPERS
#*********************
async def check_if_user_can_interact_with_view(interaction, interaction_lock, message_author):
    # Check if we're already processing an interaction
    if interaction_lock.locked():
        await interaction.response.send_message("Please wait for the current action to complete.", ephemeral=True)
        return False

    if interaction.user.id != message_author:
        await interaction.response.send_message("Only the user who used this command may interact with this screen.", ephemeral=True)
        return False

    return True


# Placeholder button that does nothing when clicked
def create_dummy_label_button(label_text, row=1):
    button = discord.ui.Button(
        label=f"{label_text}",
        style=discord.ButtonStyle.gray,
        row=row
    )
    button.callback = dummy_callback()
    return button
def dummy_callback():
    async def callback(interaction):
        # Just acknowledge the interaction to prevent the "interaction failed" message
        # Without doing anything else
        await interaction.response.defer(ephemeral=True, thinking=False)
    return callback


# Retry decorator for handling SSL errors
def retry_on_ssl_error(max_retries=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except discord.errors.InteractionResponded:
                    # Interaction already responded to, so don't retry
                    return
                except aiohttp.client_exceptions.ClientOSError as e:
                    if "SSL" in str(e) and retries < max_retries - 1:
                        retries += 1
                        await asyncio.sleep(delay)
                    else:
                        # If we've exhausted retries or it's not an SSL error, re-raise
                        raise
        return wrapper
    return decorator