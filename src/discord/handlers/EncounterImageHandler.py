from PIL import Image, ImageFilter, ImageDraw, ImageFont

from src.commons.CommonFunctions import build_image_file, load_font
from src.resources.constants.TGO_MMO_constants import *


class EncounterImageHandler:
    def __init__(self, background_img_path: str, foreground_img_path: str, text: str):
        self.background_img_path = background_img_path
        self.foreground_img_path = foreground_img_path
        self.text = text

        self.background_img = Image.open(self.background_img_path)
        self.foreground_img = Image.open(self.foreground_img_path)
        self.textbox_img = Image.open(build_image_file(TEXT_BOX_IMAGE).filename)

        self.creature_name_font_regular = load_font(font_path = build_image_file(FONT_FOREST_REGULAR_PATH).filename, font_size = CREATURE_NAME_TEXT_SIZE)
        self.creature_name_font_bold = load_font(font_path = build_image_file(FONT_FOREST_BOLD_PATH).filename, font_size = CREATURE_NAME_TEXT_SIZE)
        self.supporting_text_font = load_font(font_path = build_image_file(FONT_FOREST_REGULAR_PATH).filename, font_size = SUPPORTING_TEXT_SIZE)


    def handle_image(self, image_path):
        # Logic to handle encounter images
        pass

    # handler for generating encounter image
    def create_encounter_image(self):
        # Resize the foreground image to 80% of its size
        self.foreground_img = self.foreground_img.resize((int(self.foreground_img.width * FOREGROUND_IMAGE_RESIZE_PERCENT), int(self.foreground_img.height * FOREGROUND_IMAGE_RESIZE_PERCENT)), Image.LANCZOS)

        # Create a copy of the background
        final_img = self.background_img.copy()

        # Paste the foreground onto the background
        foreground_image_with_border = self.add_outline_to_img(self.foreground_img)
        foreground_image_offset = self.get_foreground_image_offset(self.foreground_img, self.background_img)
        final_img.paste(foreground_image_with_border, foreground_image_offset, foreground_image_with_border)


        # Add text for creature name
        self.add_text_to_image(
            base_img=final_img.copy(),
            font=self.creature_name_font_regular,
            max_width=final_img.width - (2 * 30),
        )

        #Display the result
        final_img.show()

        return final_img


    # set up text to add to encounter image
    def add_text_to_image(self, base_img: Image, font: ImageFont, max_width:int):
        draw = ImageDraw.Draw(base_img)

        # Split text into words
        creature_text = self.split_lines('Creature Name', draw, font, max_width)
        wild_text = self.split_lines('A Wild', draw, font, max_width)
        appears_text = self.split_lines('Appears', draw, font, max_width)

        # Draw each line of text
        self.place_text_on_image(lines=creature_text, font=self.creature_name_font_bold, outline_width=2, draw=draw, padding=(0, 126), add_border=True, center_text=True, text_box_width=base_img.width, text_color=FONT_COLOR_BLACK, outline_color=FONT_COLOR_WHITE)
        self.place_text_on_image(lines=wild_text, font=self.supporting_text_font, outline_width=2, draw=draw, padding=(-126, 126), add_border=False, center_text=True, text_box_width=base_img.width, text_color=FONT_COLOR_WHITE, outline_color=FONT_COLOR_WHITE)
        self.place_text_on_image(lines=appears_text, font=self.supporting_text_font, outline_width=2, draw=draw, padding=(126, 126), add_border=False, center_text=True, text_box_width=base_img.width, text_color=FONT_COLOR_WHITE, outline_color=FONT_COLOR_WHITE)


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


    # Calculate position to center the foreground on the background And move it down by 50 pixels
    def get_foreground_image_offset(self, foreground: Image, background_img: Image):
        return (background_img.width - foreground.width) // 2, ((background_img.height - foreground.height) // 2) + 50

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


