import asyncio
import functools
import os
import random

import aiohttp
import discord
import io

import requests
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageChops
from discord import File

from src.resources.constants.TGO_MMO_constants import FONT_COLOR_BLACK, FONT_COLOR_WHITE
from src.resources.constants.file_paths import PLAYER_PROFILE_AVATAR_FALLBACK_1_IMAGE, PLAYER_PROFILE_AVATAR_FALLBACK_2_IMAGE
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
#-------------------------------IMAGE FUNCTIONS----------------------------------------------
#************************************************************************************
def to_grayscale(discord_file, file_name=None) -> discord.File:
    discord_file.fp.seek(0)
    img = Image.open(discord_file.fp)
    if img.mode in ("RGBA", "LA"):
        img = img.convert("LA")  # Grayscale + alpha
    else:
        img = img.convert("L")  # Grayscale only
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return discord.File(buf, filename=file_name if file_name else discord_file.filename)


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

    x = center_pixel_location[0] - text_width // 2
    y = center_pixel_location[1] - text_height // 2
    return (x, y)

def open_image_from_url(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        img = Image.open(io.BytesIO(response.content))
        return img
    else:
        return Image.open(PLAYER_PROFILE_AVATAR_FALLBACK_1_IMAGE if random.random() > 0.5 else PLAYER_PROFILE_AVATAR_FALLBACK_2_IMAGE)



# puts a colored border around an input image
def add_border_to_image(base_image: Image.Image, text: str, font: ImageFont, border_size: int = 10, border_color: tuple = (0, 0, 0, 255), font_color: tuple = FONT_COLOR_WHITE):
    image_draw = ImageDraw.Draw(base_image)

    # Draw border - the color #006891 with alpha
    for offset_x in range(-1 * border_size, border_size + 1):
        for offset_y in range(-1 * border_size, border_size + 1):
            if abs(offset_x) == border_size or abs(offset_y) == border_size:  # Only draw the border edge
                image_draw.text((border_size + offset_x, border_size + offset_y), text, font=font, fill=border_color)

    # Draw text on top
    image_draw.text((border_size, border_size), text, font=font, fill=font_color)
    return base_image


# adds a gaussian blur mask to the edges of an image
def add_blur_mask_to_image(self, image: Image.Image):
        # Create an alpha mask based on the image's alpha channel
        r, g, b, a = image.split()

        # Create a mask with padding from the edges
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)

        # Draw a slightly smaller rectangle with padding from the edges
        padding = 20  # Adjust this value to control feather width
        draw.rectangle((
            padding,
            padding,
            image.width - padding,
            image.height - padding
        ), fill=255)

        # Apply feathering (blur the mask edges)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=15))

        # Combine the original alpha with our feathered mask
        new_a = ImageChops.multiply(a, mask)

        # Apply the new alpha channel
        image.putalpha(new_a)

        return image

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

def resize_text_to_fit_with_newlines(text, draw, font, max_width, min_font_size=10, allow_newlines=False, max_lines=5):
    current_font = font
    current_font_size = font.size
    current_text = text

    # Check if the text already fits on one line
    text_width = draw.textlength(text, font=current_font)

    if text_width <= max_width:
        return current_font, text

    # If newlines are allowed, try word wrapping first
    if allow_newlines and max_lines > 1:
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_width = draw.textlength(test_line, font=current_font)

            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word

                    # Check if we've reached max lines
                    if len(lines) >= max_lines:
                        # Truncate the last line if needed
                        if len(lines) == max_lines:
                            ellipsis = "..."
                            last_line = lines[-1]
                            while draw.textlength(last_line + ellipsis, font=current_font) > max_width and len(
                                    last_line) > 0:
                                last_line = last_line[:-1]
                            lines[-1] = last_line + ellipsis if last_line else ellipsis
                        break
                else:
                    # Single word is too long, handle it separately
                    current_line = word

        # Add the last line if we haven't exceeded max_lines
        if current_line and len(lines) < max_lines:
            lines.append(current_line)

        # Check if wrapped text fits
        wrapped_text = "\n".join(lines)
        max_line_width = max(draw.textlength(line, font=current_font) for line in lines)

        if max_line_width <= max_width and len(lines) <= max_lines:
            return current_font, wrapped_text

    # If text doesn't fit or newlines aren't allowed, try reducing font size
    while text_width > max_width and current_font_size > min_font_size:
        current_font_size -= 1

        # Create a new font with smaller size
        try:
            current_font = ImageFont.truetype(font.path, current_font_size)
        except IOError:
            current_font = ImageFont.load_default()

        # Re-check with newlines if allowed
        if allow_newlines and max_lines > 1:
            words = text.split()
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_width = draw.textlength(test_line, font=current_font)

                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                        if len(lines) >= max_lines:
                            break
                    else:
                        current_line = word

            if current_line and len(lines) < max_lines:
                lines.append(current_line)

            wrapped_text = "\n".join(lines[:max_lines])
            max_line_width = max(draw.textlength(line, font=current_font) for line in lines[:max_lines])

            if max_line_width <= max_width:
                return current_font, wrapped_text
        else:
            text_width = draw.textlength(text, font=current_font)

    # If reducing font size didn't work, truncate the text
    if not allow_newlines or max_lines == 1:
        if draw.textlength(text, font=current_font) > max_width:
            ellipsis = "..."
            truncated_text = text

            while draw.textlength(truncated_text + ellipsis, font=current_font) > max_width and len(truncated_text) > 0:
                truncated_text = truncated_text[:-1]

            current_text = truncated_text + ellipsis if truncated_text else ellipsis

    return current_font, current_text

#************************************************************************************
#-------------------------------DISCORD FUNCTIONS------------------------------------
#************************************************************************************
def get_user_discord_profile_pic(user = None):
    avatar_url = user.display_avatar.url if hasattr(user,'display_avatar') else user.avatar.url if user.avatar else user.default_avatar.url
    return avatar_url


#*********************
# DISCORD VIEW HELPERS
#*********************
async def check_if_user_can_interact_with_view(interaction, interaction_lock, message_author_id):
    # Check if we're already processing an interaction
    if interaction_lock.locked():
        await interaction.response.send_message("Please wait for the current action to complete.", ephemeral=True)
        return False

    if message_author_id and interaction.user.id != message_author_id:
        await interaction.response.send_message("You do not have permission to interact with this command, freak.", ephemeral=True)
        return False

    return True


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


#************************************************************************************
#-------------------------------BUTTON FUNCTIONS------------------------------------
#************************************************************************************
# Button that goes back to parent view when clicked
def create_go_back_button(original_view, row=2, interaction_lock=None, message_author_id=None):
    button = discord.ui.Button(label="⬅️ Go Back", style=discord.ButtonStyle.red, row=row)
    button.callback = go_back_callback(original_view=original_view, interaction_lock=interaction_lock, message_author_id=message_author_id,)
    return button
def go_back_callback(original_view, interaction_lock=None, message_author_id=None):
    @retry_on_ssl_error(max_retries=3, delay=1)
    async def callback(interaction):
        # Check if we're already processing an interaction
        if not await check_if_user_can_interact_with_view(interaction, interaction_lock, message_author_id):
            return

    # Acquire lock to prevent concurrent actions
        async with interaction_lock:
            await interaction.response.defer()

    # Go back to the previous view or state
        await interaction.message.edit(attachments=[], view=original_view)
    return callback


def create_close_button(interaction_lock, message_author_id, row=1):
    button = discord.ui.Button(
        label="✘",
        style=discord.ButtonStyle.red,
        row=row
    )

    @retry_on_ssl_error(max_retries=3, delay=1)
    async def close_callback(interaction):
        if not await check_if_user_can_interact_with_view(interaction, interaction_lock, message_author_id):
            return

        async with interaction_lock:
            await interaction.message.delete()

    button.callback = close_callback
    return button

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

# Creates an invisible button that serves as a spacer
def create_spacer_button(row=0):
    button = discord.ui.Button(
        label="\u200b",  # Zero-width space character
        style=discord.ButtonStyle.gray,
        disabled=True,
        row=row
    )
    # Make the button almost invisible
    button.callback = dummy_callback()
    return button

#************************************************************************************
#-------------------------------SQL FUNCTIONS------------------------------------
#************************************************************************************
def get_query_connector(query: str):
    return " WHERE " if ('where' in query) else " AND "

#************************************************************************************
#-------------------------------GENERAL FUNCTIONS------------------------------------
#************************************************************************************
def flip_coin(iteration: int=1, total_iterations: int=1):
    if random.random() > 0.5:
        return flip_coin(iteration=iteration + 1, total_iterations=total_iterations) if iteration < total_iterations else True
    return False

def pad_text(text, desired_length):
    if len(text) < desired_length:
        # Fill with non-breaking space (‎) characters to reach exactly 18
        return text + "‎" * (desired_length - len(text))
    elif len(text) > desired_length:
        # Truncate if longer than 18
        return text[:desired_length]
    else:
        return text

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def convert_date_format_to_month_name(date_str: str, current_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    if date_str is not None and date_str != "Unknown":
        try:
            from datetime import datetime
            catch_date = datetime.strptime(date_str, current_format)
            day = catch_date.day
            # Add suffix to day (1st, 2nd, 3rd, etc.)
            if 11 <= day <= 13:
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
            month_abbr = catch_date.strftime("%b")
            formatted_date = f"{month_abbr} {day}{suffix} {catch_date.year}"
        except (ValueError, TypeError):
            formatted_date = date_str

        return formatted_date
    return "Unknown"