from PIL import Image, ImageFilter, ImageFont
import os

from PIL import Image, ImageDraw, ImageOps
import os
import numpy as np

from src.commons.CommonFunctions import get_user_discord_profile_pic
from src.resources.constants.file_paths import *


def create_encyclopedia_image(user):
    # generate encyclopedia page
    encyclopedia_img = Image.open(f"{ENCYCLOPEDIA_BG_BASE}_1.png")

    # get user's profile pic
    profile_pic = Image.open(get_user_discord_profile_pic(user)).convert("RGBA")
    # Resize profile pic to half the size
    width, height = profile_pic.size
    profile_pic = profile_pic.resize((width // 2, height // 2), Image.LANCZOS)
    encyclopedia_img.paste(profile_pic, (0, 0), profile_pic)

    # Paste the shadow onto the final image
    textbox_shadow_img = Image.open(ENCYCLOPEDIA_TEXT_SHADOW_IMAGE)
    encyclopedia_img.paste(textbox_shadow_img, (0, 0), textbox_shadow_img)

    # Paste the general overlay onto the final image
    overlay_img = Image.open(ENCYCLOPEDIA_OVERLAY_IMAGE)
    encyclopedia_img.paste(overlay_img, (0, 0), overlay_img)

    # Display the result
    encyclopedia_img.show()


def create_encounter_image(background_img_path, foreground_img_path):
    # Open the images
    background = Image.open(background_img_path)
    foreground = Image.open(foreground_img_path)
    text_box = Image.open(r"C:\Users\Ryan\PycharmProjects\3rdParty\Bumbot_SketchingAlley_TGO_MMO\src\resources\images\env_textbox.png")

    # Resize the foreground image to 80% of its size
    foreground = foreground.resize((int(foreground.width * 0.8), int(foreground.height * 0.8)), Image.LANCZOS)

    # Calculate position to center the foreground on the background And move it down by 50 pixels
    position = ((background.width - foreground.width) // 2, ((background.height - foreground.height) // 2) + 50)

    # Create a copy of the background
    final_img = background.copy()

    # Paste the foreground onto the background
    foreground_image_with_border = add_border_to_img(foreground)
    final_img.paste(foreground, position, foreground)

    # Paste the foreground onto the background
    final_img.paste(text_box, (0,0), text_box)

    # Add text if provided
    text = 'Black Bear'
    font_path = r"C:\Users\Ryan\PycharmProjects\3rdParty\Bumbot_SketchingAlley_TGO_MMO\src\resources\fonts\NationalForestPrintRegular.otf"
    font_path_bold = r"C:\Users\Ryan\PycharmProjects\3rdParty\Bumbot_SketchingAlley_TGO_MMO\src\resources\fonts\NationalForestPrintBold.otf"
    font_size = 30
    text_color = (0, 0, 0)  # Black text
    text_padding = (30, 30)  # Adjust padding as needed


    # Get the dimensions of the text box to determine text placement
    max_width = final_img.width - (2 * text_padding[0])
    text_box_width = 426

    # Add text to the image
    final_img = add_text_to_image(image=final_img.copy(),text=text,font=load_font(font_path, font_size),text_color=text_color, max_width=140, x_offset=20,y_offset=20)

    # Display the result
    final_img.show()

    return final_img


def add_border_to_img(foreground, shadow_radius=2, shadow_offset=2, shadow_opacity=255):
    # Ensure the foreground is in RGBA mode
    if foreground.mode != 'RGBA':
        foreground = foreground.convert('RGBA')

    # Create a new image for the final result
    result = Image.new('RGBA', foreground.size, (0, 0, 0, 0))

    # Create three shadow layers with different parameters
    for i in range(30):
        # Create a new image for this shadow layer
        shadow = Image.new('RGBA', foreground.size, (0, 0, 0, 0))

        # Create a mask from the alpha channel of the foreground
        alpha_mask = foreground.split()[3]

        # Create the shadow layer with white
        shadow_layer = Image.new('RGBA', foreground.size, (255, 255, 255, shadow_opacity))
        shadow.paste(shadow_layer, (shadow_offset, shadow_offset), alpha_mask)
        shadow.paste(shadow_layer, (shadow_offset, -shadow_offset), alpha_mask)
        shadow.paste(shadow_layer, (-shadow_offset, shadow_offset), alpha_mask)
        shadow.paste(shadow_layer, (-shadow_offset, -shadow_offset), alpha_mask)

        # Apply Gaussian blur to the shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_radius))

        # Paste the shadow onto the result
        result.paste(shadow, (0, 0), shadow)

    # Paste the foreground on top
    # After the for loop, color all pixels in result as white while preserving alpha
    width, height = result.size
    for y in range(height):
        for x in range(width):
            _, _, _, a = result.getpixel((x, y))
            if a > 0:  # Only modify non-transparent pixels
                result.putpixel((x, y), (255, 255, 255, a))

    result.filter(ImageFilter.GaussianBlur(radius=shadow_radius))
    result.paste(foreground, (0, 0), foreground)

    return result


def add_text_to_image(image, text, font, text_color, x_offset, y_offset, max_width, outline_color=(255, 255, 255), outline_width=2):
    # Create a draw of the image
    draw = ImageDraw.Draw(image)


    font_path_bold = r"C:\Users\Ryan\PycharmProjects\3rdParty\Bumbot_SketchingAlley_TGO_MMO\src\resources\fonts\NationalForestPrintBold.otf"


    main_font = load_font(font_path = font_path_bold, font_size = 30)
    max_width = 220

    main_font = resize_text_to_fit(text=text, draw=draw, font=main_font, max_width=max_width, min_font_size=10, font_path=font.path)

    support_font = load_font(font_path = font.path, font_size = 14)
    support_font_2 = load_font(font_path = font.path, font_size = 18)

    # lines = split_lines(text=text, draw=draw, font=main_font, max_width=max_width)

    # Draw text with outline
    draw_font(lines=[main_font[1]], font=main_font[0], outline_width=1, draw=draw, padding=(0, 124), add_border= True, center_text=True, text_box_width=image.width, text_color=text_color, outline_color=outline_color)
    draw_font(lines=['A Wild'], font=support_font_2, outline_width=outline_width, draw=draw, padding=(-140, 128), add_border= False, center_text=True, text_box_width=image.width, text_color=text_color, outline_color=outline_color)
    draw_font(lines=['Appears!!'], font=support_font, outline_width=outline_width, draw=draw, padding=(140, 130), add_border= False, center_text=True, text_box_width=image.width, text_color=text_color, outline_color=outline_color)

    return image


def load_font(font_path, font_size):
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
    return font


def split_lines(text, draw, font, max_width):
    words = text.split()
    lines = []
    current_line = []

    # Create wrapped lines
    for word in words:
        # Try adding the word to the current line
        test_line = ' '.join(current_line + [word])
        text_width = draw.textlength(test_line, font=font)

        if text_width <= max_width:
            current_line.append(word)
        else:
            # Line is full, start a new line
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # This happens when a single word is longer than max_width
                lines.append(word)
                current_line = []

    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))

    return lines


def resize_text_to_fit(text, draw, font, max_width, min_font_size=10, font_path=None):
    current_font = font
    current_font_size = font.size
    current_text = text

    # Check if the text already fits
    text_width = draw.textlength(text, font=current_font)

    if text_width <= max_width:
        return current_font, current_text

    # If text doesn't fit, try reducing font size
    while text_width > max_width and current_font_size > min_font_size:
        current_font_size -= 1

        # Create a new font with smaller size
        if font_path:
            try:
                current_font = ImageFont.truetype(font_path, current_font_size)
            except IOError:
                current_font = ImageFont.load_default()
        else:
            # If no font path is provided, we can't resize the font
            # In this case, truncate the text instead
            break

        text_width = draw.textlength(text, font=current_font)

    # If reducing font size didn't work or wasn't possible, truncate the text
    if text_width > max_width:
        # Truncate text with ellipsis
        ellipsis = "..."
        truncated_text = text

        while draw.textlength(truncated_text + ellipsis, font=font) > max_width and len(truncated_text) > 0:
            truncated_text = truncated_text[:-1]

        current_text = truncated_text + ellipsis if truncated_text else ellipsis

    return current_font, current_text


def draw_font(lines, font, outline_width, draw, padding, add_border=False, center_text=False, text_box_width=None, text_color=(0, 0, 0), outline_color=(255, 255, 255)):
    # Draw text with outline
    x_offset = padding[0]
    y_offset = padding[1]
    line_height = font.size + 4  # Add a little extra space between lines

    for line in lines:
        current_x_offset = (text_box_width - draw.textlength(line, font=font)) // 2 + x_offset

        # Draw outline by rendering the text multiple times with offsets
        if add_border:
            for border_offset_x in range(-outline_width, outline_width + 1):
                for border_offset_y in range(-outline_width, outline_width + 1):
                    # Skip the center position (that will be the main text)
                    if border_offset_x == 0 and border_offset_y == 0:
                        continue
                    draw.text((current_x_offset + border_offset_x, y_offset + border_offset_y), line, font=font, fill=outline_color)


        # Draw the main text on top
        draw.text((current_x_offset, y_offset), line, font=font, fill=text_color)
        y_offset += line_height


if __name__ == "__main__":
    background_path = r"C:\Users\Ryan\PycharmProjects\3rdParty\Bumbot_SketchingAlley_TGO_MMO\src\resources\images\forest_est_1.png"
    foreground_path = r"C:\Users\Ryan\PycharmProjects\3rdParty\Bumbot_SketchingAlley_TGO_MMO\src\resources\images\Deer_2_THUMB.png"

    # Optional: Save the resulting image
    output_dir = os.path.dirname(background_path)
    output_path = os.path.join(output_dir, "combined_image.png")

    # Overlay the images and display the result
    create_encyclopedia_image()

    # create_encounter_image(background_path, foreground_path)