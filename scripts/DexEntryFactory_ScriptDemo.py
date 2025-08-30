import os

from PIL import Image, ImageDraw, ImageFont

from src.resources.constants.general_constants import IMAGE_FOLDER_IMAGES, IMAGE_FOLDER_BASE_PATH

folder_location = r"C:\Users\Ryan\PycharmProjects\3rdParty\Bumbot_SketchingAlley_TGO_MMO\src\resources\images\encyclopedia_resources\dex_icons"

icon_overlay_path = r"/src/resources/images/encyclopedia_resources/dex_icons/DexIcon_Overlay.png"
icon_shadow_path = r"/src/resources/images/encyclopedia_resources/dex_icons/DexIcon_BGShadow.png"
icon_stats_overlay_path = r"/src/resources/images/encyclopedia_resources/dex_icons/DexIcon_StatsBar.png"

icon_stats_locked_icon_path = r"DexIcon_Critter_LockedIcon.png"
icon_stats_critter_rabbit_icon_path = r"DexIcon_Creature_Rabbit_3_1.png"

icon_stats_common_bg_path = r"/src/resources/images/encyclopedia_resources/dex_icons/DexIcon_BackgroundColor_Common.png"
icon_stats_uncommon_bg_path = r"/src/resources/images/encyclopedia_resources/dex_icons/DexIcon_BackgroundColor_Uncommon.png"
icon_stats_rare_bg_path = r"/src/resources/images/encyclopedia_resources/dex_icons/DexIcon_BackgroundColor_Rare.png"
icon_stats_epic_bg_path = r"/src/resources/images/encyclopedia_resources/dex_icons/DexIcon_BackgroundColor_Epic.png"
icon_stats_legendary_bg_path = r"/src/resources/images/encyclopedia_resources/dex_icons/DexIcon_BackgroundColor_Legendary.png"
icon_stats_mythic_bg_path = r"/src/resources/images/encyclopedia_resources/dex_icons/DexIcon_BackgroundColor_Mythical.png"


def dex_entry_factory_script(rarity="Common", show_stats=False, creature_name="Rabbit", dex_num = '01', creature_is_locked=True, total_catches=0, total_mythical_catches=0):
    icon_overlay = Image.open(icon_overlay_path)

    # Create a copy of the background to serve as the canvas
    final_img = Image.open(get_image_path(image_name = f"DexIcon_BackgroundColor_{rarity}.png",folder_location=folder_location))

    # Paste the shadow onto the final image
    icon_shadow = Image.open(icon_shadow_path)
    final_img.paste(icon_shadow, (0,0), icon_shadow)

    # Paste the creature icon onto the final image

    creature_img = Image.open(get_image_path(image_name = icon_stats_locked_icon_path if creature_is_locked else icon_stats_critter_rabbit_icon_path,folder_location=folder_location))

    # if not creature_is_locked:
    #     temp_img = Image.open(r"C:\Users\Ryan\PycharmProjects\3rdParty\Bumbot_SketchingAlley_TGO_MMO\src\resources\images\Rabbit_1_THUMB.png")
    #     temp_img = Image.open(r"C:\Users\Ryan\PycharmProjects\3rdParty\Bumbot_SketchingAlley_TGO_MMO\src\resources\images\Raccoon_1_THUMB.png")
    #     final_img = format_creature_image(dex_icon=final_img, creature_image=temp_img)

    final_img.paste(creature_img, (0,0), creature_img)

    if creature_is_locked: # if the creature is locked, we don't show stats
        show_stats = False

    if show_stats:
        icon_stats_overlay = Image.open(icon_stats_overlay_path)
        final_img.paste(icon_stats_overlay, (0, 0), icon_stats_overlay)

    # add the final overlay on top
    icon_overlay = Image.open(icon_overlay_path)
    final_img.paste(icon_overlay, (0, 0), icon_overlay)

    add_text_to_image(image= final_img, dex_num= dex_num, total_catches=total_catches, total_mythical_catches=total_mythical_catches, creature_is_locked=creature_is_locked).show()

def add_text_to_image(image: Image.Image, dex_num: str, total_catches=0, total_mythical_catches=0, creature_is_locked=False):
    image = add_dex_num_to_image(image, dex_num=dex_num)

    if not creature_is_locked:
        image = add_stats_to_image(image, total_catches=total_catches, total_mythical_catches=total_mythical_catches)
    return image


def add_stats_to_image(image: Image.Image, total_catches=0, total_mythical_catches=0, color: tuple = (0, 0, 0)):
    font_path_bold = r"/src/resources/fonts/NationalForestPrintBold.otf"
    draw = ImageDraw.Draw(image)
    stats_num_font = ImageFont.truetype(font_path_bold, 12)

    # Draw the total catches
    draw.text((81, 64), f"{total_catches}", fill=(0, 0, 0), font=stats_num_font, anchor="mm")
    draw.text((58, 64), f"{total_mythical_catches}", fill=(255, 255, 255), font=stats_num_font, anchor="mm")
    return image


def add_dex_num_to_image(image: Image.Image, dex_num ='01'):
    font_path_bold = r"/src/resources/fonts/NationalForestPrintBold.otf"
    draw = ImageDraw.Draw(image)

    # draw the dex number
    dex_num_font = ImageFont.truetype(font_path_bold, 26)

    # Center X position
    x_center, y_center = 15, 38

    # Get actual height of each character to calculate precise positioning
    char_heights = []
    for digit in dex_num:
        bbox = dex_num_font.getbbox(digit)
        height = bbox[3] - bbox[1]
        char_heights.append(height)


    # Calculate vertical offset to center all characters around y_center
    num_chars = len(dex_num)
    line_height = 26  # Roughly the height of each character with font size 26
    total_height = line_height * num_chars
    start_y = y_center - (total_height / 2) + (line_height / 2)

    # Draw each digit on a new line
    for i, digit in enumerate(dex_num):
        # Position each character vertically
        y = start_y + (i * line_height)
        draw.text((x_center, y), digit, fill=(0, 0, 0), font=dex_num_font, anchor="mm")

    return image


def get_image_path(image_name: str, folder_location: str = IMAGE_FOLDER_IMAGES) -> str:
    path = os.path.join(os.path.join(IMAGE_FOLDER_BASE_PATH, folder_location))
    return os.path.join(os.path.join(path, image_name))


def format_creature_image(dex_icon: Image.Image, creature_image: Image.Image) -> Image.Image:
    # Resize the creature image to fit within the dex icon
    creature_image = creature_image.resize((128, 128))

    # Calculate position to center the creature image on the dex icon
    dex_icon_width, dex_icon_height = dex_icon.size
    creature_width, creature_height = creature_image.size
    position = (((dex_icon_width - creature_width) // 2) + 28, ((dex_icon_height - creature_height) // 2) + 10)

    # Paste the creature image onto the dex icon with transparency handling
    dex_icon.paste(creature_image, position, creature_image)

    return dex_icon


if __name__ == "__main__":
    background_path = r"/src/resources/images/forest_est_1.png"
    foreground_path = r"/src/resources/images/Deer_2_THUMB.png"

    # Optional: Save the resulting image
    output_dir = os.path.dirname(background_path)
    output_path = os.path.join(output_dir, "combined_image.png")

    # Overlay the images and display the result
    dex_entry_factory_script(rarity="Common", show_stats=True, creature_name="Rabbit", creature_is_locked=False, total_catches=999, total_mythical_catches=99, dex_num='01')
    # dex_entry_factory_script(rarity="Common", show_stats=True, creature_name="Rabbit", creature_is_locked=True, total_catches=999, total_mythical_catches=99, dex_num='01')
    # dex_entry_factory_script(rarity="Rare", show_stats=True, creature_name="Rabbit", creature_is_locked=False, total_catches=13, total_mythical_catches=114, dex_num='99')
    # dex_entry_factory_script(rarity="Uncommon", show_stats=True, creature_name="Rabbit", creature_is_locked=False, total_catches=7, total_mythical_catches=4, dex_num='12')
    # dex_entry_factory_script(rarity="Epic", show_stats=True, creature_name="Rabbit", creature_is_locked=True, total_catches=123, total_mythical_catches=4, dex_num='88')
    # dex_entry_factory_script(rarity="Legendary", show_stats=True, creature_name="Rabbit", creature_is_locked=True, total_catches=123, total_mythical_catches=4, dex_num='77')
    # dex_entry_factory_script(rarity="Mythical", show_stats=True, creature_name="Rabbit", creature_is_locked=True, total_catches=123, total_mythical_catches=4, dex_num='00')