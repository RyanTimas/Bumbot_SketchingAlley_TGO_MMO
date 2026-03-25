import asyncio
import functools
import os
import random
import ssl

import aiohttp
import discord
import io

import requests
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageChops
from discord import File, app_commands

from src.resources.constants.TGO_MMO_constants import FONT_COLOR_BLACK, FONT_COLOR_WHITE
from src.resources.constants.file_paths import *
from src.resources.constants.general_constants import IMAGE_FOLDER_BASE_PATH, IMAGE_FOLDER_IMAGES, DISCORD_USER_WHITELIST

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


def add_text_to_image(image: Image, font, text: str = "", position= (0,0), color: tuple = FONT_COLOR_BLACK):
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


def center_image_on_image(foreground_image: Image, background_image: Image, center_pixel: tuple = None):
    bg_width, bg_height = background_image.size
    fg_width, fg_height = foreground_image.size

    if center_pixel is None:
        # Default behavior - center on the background image
        x = (bg_width - fg_width) // 2
        y = (bg_height - fg_height) // 2
    else:
        # Center the foreground image on the specified pixel location
        center_x, center_y = center_pixel
        x = center_x - (fg_width // 2)
        y = center_y - (fg_height // 2)

    return (x, y)
def open_image_from_url(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        img = Image.open(io.BytesIO(response.content))
        return img
    else:
        return Image.open(PLAYER_PROFILE_AVATAR_FALLBACK_1_IMAGE if random.random() > 0.5 else PLAYER_PROFILE_AVATAR_FALLBACK_2_IMAGE)

def add_border_to_image(base_image: Image, text: str, font: ImageFont, border_size: int = 10, border_color: tuple = (0, 0, 0, 255), font_color: tuple = FONT_COLOR_WHITE):
    image_draw = ImageDraw.Draw(base_image)

    # Draw border - the color #006891 with alpha
    for offset_x in range(-1 * border_size, border_size + 1):
        for offset_y in range(-1 * border_size, border_size + 1):
            if abs(offset_x) == border_size or abs(offset_y) == border_size:  # Only draw the border edge
                image_draw.text((border_size + offset_x, border_size + offset_y), text, font=font, fill=border_color)

    # Draw text on top
    image_draw.text((border_size, border_size), text, font=font, fill=font_color)
    return base_image

def add_blur_mask_to_image(image: Image):
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

def build_user_profile_pic(user, size=(600, 600)):
    # get user's profile pic
    profile_pic_avatar_url = get_user_discord_profile_pic(user)
    response = requests.get(profile_pic_avatar_url)

    profile_pic = Image.open(io.BytesIO(response.content)).convert("RGBA")
    profile_pic = profile_pic.resize(size, Image.LANCZOS)

    # profile_pic = self.add_blur_mask_to_image(profile_pic)

    return profile_pic


#*********************
# DISCORD VIEW HELPERS
#*********************
async def check_if_user_can_interact_with_view(interaction, interaction_lock, target_user_id):
    # Check if we're already processing an interaction
    if interaction_lock.locked():
        await interaction.response.send_message("Please wait for the current action to complete.", ephemeral=True)
        return False

    if target_user_id and interaction.user.id != target_user_id:
        await interaction.response.send_message("You do not have permission to interact with this, freak.", ephemeral=True)
        return False

    return True

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

#****************************************************************************************
#---------------------------------------IMAGE FUNCTION--------------------------------------------
#****************************************************************************************
def place_username_on_image(target_user, image: Image, border_color = (0, 104, 145), font_color = FONT_COLOR_WHITE, max_font_size = 50, max_width = 300):
        draw = ImageDraw.Draw(image)
        font = resize_text_to_fit(text=target_user.nickname, draw=draw, font=ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, max_font_size), max_width=max_width, min_font_size=10)

        # Get text dimensions
        text_bbox = draw.textbbox((0, 0), target_user.nickname, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Create a separate image for the text with border
        text_img = Image.new('RGBA', (text_width + 8, text_height + 8), (0, 0, 0, 0))
        x_offset, y_offset = 11, 10
        border_size = 4
        username_font_image = add_border_to_image(base_image=text_img, text=target_user.nickname, font=font, border_size=border_size, border_color=border_color, font_color=font_color)

        # Paste the text image onto the profile image
        image.paste(username_font_image, (x_offset - border_size, y_offset - border_size), username_font_image)
        return image


#************************************************************************************
#---------------------------------------DECORATORS--------------------------------------------
#************************************************************************************
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

def admin_only():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id not in DISCORD_USER_WHITELIST:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True, delete_after=5)
            return False
        return True
    return app_commands.check(predicate)

def interaction_guard(self=None, max_retries=3, delay=1, defer_response=True):
    def decorator(func):
        async def wrapper(interaction):
            if not self:
                return await func(interaction)

            if await check_if_user_can_interact_with_view(interaction, self.interaction_lock, getattr(self, 'message_author', None).user_id):
                async with self.interaction_lock:
                    if defer_response:
                        await interaction.response.defer()

                    for attempt in range(max_retries):
                        try:
                            return await func(interaction)
                        except ssl.SSLError as e:
                            if attempt == max_retries - 1:
                                raise e
                            await asyncio.sleep(delay)
        return wrapper
    return decorator