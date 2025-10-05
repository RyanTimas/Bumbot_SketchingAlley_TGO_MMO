import random

from PIL import Image, ImageFilter, ImageDraw, ImageFont

from PIL import Image, ImageFilter, ImageDraw, ImageFont

from src.commons.CommonFunctions import convert_to_png, resize_text_to_fit
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class EncounterImageHandler:
    def __init__(self, creature: TGOCreature, environment: TGOEnvironment = None, time_of_day: str = DAY):
        self.creature = creature
        self.environment = environment
        self.time_of_day = time_of_day if time_of_day else DAY

    # handler for generating encounter image
    def create_encounter_image(self):
        foreground_img = Image.open(f"{IMAGE_FOLDER_CREATURES_PATH}\\{self.creature.img_root}{ENCOUNTER_SCREEN_THUMBNAIL_SUFFIX}")

        time_of_day_suffix = '' if self.time_of_day in (DAY, NIGHT) or not self.time_of_day else f'_{self.time_of_day}'
        final_img = Image.open(f"{ENCOUNTER_SCREEN_ENVIRONMENT_BG_ROOT}{self.environment.dex_no}_{self.environment.variant_no}{time_of_day_suffix}{IMAGE_FILE_EXTENSION}")

        textbox_img = Image.open(ENCOUNTER_SCREEN_TEXT_BOX_IMAGE)
        camera_overlay_img = Image.open(ENCOUNTER_SCREEN_CAMERA_OVERLAY_IMAGE)
        glow = self.get_glow_overlay()

        # Resize the foreground image to 80% of its size
        foreground_img = foreground_img.resize((int(foreground_img.width * ENCOUNTER_SCREEN_FOREGROUND_IMAGE_RESIZE_PERCENT), int(foreground_img.height * ENCOUNTER_SCREEN_FOREGROUND_IMAGE_RESIZE_PERCENT)), Image.LANCZOS)

        # Paste the foreground onto the background
        foreground_image_with_border = self.add_outline_to_img(foreground_img)
        foreground_image_offset = self.get_foreground_image_offset(foreground_img, final_img)
        final_img.paste(foreground_image_with_border, foreground_image_offset, foreground_image_with_border)

        if glow:
            final_img.paste(glow, (0, 0), glow)

        # Paste the textbox onto the background
        final_img.paste(camera_overlay_img, (0, 0), camera_overlay_img)
        final_img.paste(textbox_img, (0, 0), textbox_img)

        # Add text for creature name
        final_img = self.add_text_to_image(base_img=final_img.copy(),max_width=TEXT_BOX_WIDTH - (120*2),)
        return convert_to_png(final_img, 'encounter_image.png')

    def get_glow_overlay(self):
        glow_combos = {
            DAY: (None, None),
            DAWN: (ENCOUNTER_SCREEN_MORNING_GLOW_IMAGE, ENCOUNTER_SCREEN_MORNING_RAYS_IMAGE),
            DUSK: (ENCOUNTER_SCREEN_EVENING_GLOW_IMAGE, ENCOUNTER_SCREEN_EVENING_RAYS_IMAGE),
            NIGHT: (ENCOUNTER_SCREEN_NIGHT_GLOW_IMAGE, None),
        }

        glow_path = glow_combos[self.time_of_day][0]
        rays_path = glow_combos[self.time_of_day][1]

        if glow_path:
            glow = Image.open(glow_path)
            glow = Image.blend(Image.new('RGBA', glow.size, (0, 0, 0, 0)), glow, 0.6 if self.time_of_day == NIGHT else random.uniform(0.75, 0.85))
            if rays_path:
                rays = Image.open(rays_path)
                rays = Image.blend(Image.new('RGBA', rays.size, (0, 0, 0, 0)), rays, random.uniform(0.8 if self.environment.environment_id == 1 else 0.9, 0.95))
                glow.paste(rays, (0, 0), rays)
            return glow
        return None


    # set up text to add to encounter image
    def add_text_to_image(self, base_img: Image, max_width:int):
        draw = ImageDraw.Draw(base_img)

        # Split text into words
        # creature_text = self.split_lines(self.creature_name, draw, font, max_width)

        main_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, CREATURE_NAME_TEXT_SIZE)
        main_font = resize_text_to_fit(text=self.creature.name, draw=draw, font=main_font, max_width=max_width, min_font_size=10)

        support_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 14)
        support_font_2 = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 18)

        # Draw each line of text
        self.place_text_on_image(lines=[self.creature.name], font=main_font, outline_width=2, draw=draw, padding=(0, self.get_y_offset_to_center_text(main_font)), add_border=True, center_text=True, text_box_width=base_img.width, text_color=self.creature.rarity.font_color, outline_color=self.creature.rarity.outline_color)
        self.place_text_on_image(lines=['A Wild'], font=support_font_2, outline_width=2, draw=draw, padding=(-140, 128), add_border=False, center_text=True, text_box_width=base_img.width, text_color=FONT_COLOR_WHITE, outline_color=FONT_COLOR_WHITE)
        self.place_text_on_image(lines=['Appears'], font=support_font, outline_width=2, draw=draw, padding=(140, 130), add_border=False, center_text=True, text_box_width=base_img.width, text_color=FONT_COLOR_WHITE, outline_color=FONT_COLOR_WHITE)

        return base_img


    # Split text into lines that fit within the text box
    def split_lines(self, text, draw, font, max_width):
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


    def get_y_offset_to_center_text(self, font):
        target_y_position = 136

        # Calculate the vertical centering offset based on font size
        font_height = font.getbbox("Ay")[3]  # Gets approximate height including descenders
        return target_y_position - (font_height / 2)  # Center the text at the target position


    # Calculate position to center the foreground on the background And move it down by 50 pixels
    def get_foreground_image_offset(self, foreground: Image, background_img: Image):
        return (background_img.width - foreground.width) // 2, ((background_img.height - foreground.height) // 2) + ENCOUNTER_SCREEN_FOREGROUND_IMAGE_Y_OFFSET


    # draw text onto the image
    def place_text_on_image(self, lines, font, outline_width, draw, padding, add_border, center_text, text_box_width, text_color, outline_color):
        # Draw text with outline
        x_offset = padding[0]
        y_offset = padding[1]
        line_height = font.size + 4  # Add a little extra space between lines

        for line in lines:
            current_x_offset = (text_box_width - draw.textlength(line, font=font)) // 2 + x_offset

            # Draw outline by rendering the text multiple times with offsets
            if add_border:
                for border_offset_x in range(outline_width * -1, outline_width + 1):
                    for border_offset_y in range(outline_width * -1, outline_width + 1):
                        # Skip the center position (that will be the main text)
                        if border_offset_x == 0 and border_offset_y == 0:
                            continue
                        draw.text((current_x_offset + border_offset_x, y_offset + border_offset_y), line, font=font, fill=outline_color)

            # Draw the main text on top
            draw.text((current_x_offset, y_offset), line, font=font, fill=text_color)
            y_offset += line_height


    # adds a white outline with shadow to an image with transparency
    def add_outline_to_img(self, base_img: Image):
        outline_radius = 2
        outline_offset = 2
        outline_opacity = 255

        # Ensure the foreground is in RGBA mode
        if base_img != 'RGBA':
            base_img = base_img.convert('RGBA')

        # Create a new image for the final result
        img_with_outline = Image.new('RGBA', base_img.size, TRANSPARENT_IMG_BG)

        # Create many outline layer iterations to make the outline more pronounced
        for i in range(10):
            # Create a new image for this shadow layer
            outline_iteration = Image.new('RGBA', base_img.size, TRANSPARENT_IMG_BG)

            # Create a mask from the alpha channel of the foreground
            alpha_mask = base_img.split()[3]

            # Create the outline layer with white
            outline_layer = Image.new('RGBA', base_img.size, (255, 255, 255, outline_opacity))
            outline_iteration.paste(outline_layer, (outline_offset, outline_offset), alpha_mask)
            outline_iteration.paste(outline_layer, (outline_offset, outline_offset*-1), alpha_mask)
            outline_iteration.paste(outline_layer, (outline_offset*-1, outline_offset), alpha_mask)
            outline_iteration.paste(outline_layer, (outline_offset*-1, outline_offset*-1), alpha_mask)

            # Apply Gaussian blur to the shadow
            outline_iteration = outline_iteration.filter(ImageFilter.GaussianBlur(radius=outline_radius))

            # Paste the shadow onto the result
            img_with_outline.paste(outline_iteration, (0, 0), outline_iteration)

        # Paste the foreground on top
        # After the for loop, color all pixels in result as white while preserving alpha
        width, height = img_with_outline.size
        for y in range(height):
            for x in range(width):
                _, _, _, a = img_with_outline.getpixel((x, y))
                if a > 0:  # Only modify non-transparent pixels
                    img_with_outline.putpixel((x, y), (255, 255, 255, a))

        img_with_outline.filter(ImageFilter.GaussianBlur(radius=outline_radius))
        img_with_outline.paste(base_img, (0, 0), base_img)

        return img_with_outline




