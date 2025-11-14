import random

import discord

from src.resources.constants.TGO_MMO_constants import FONT_COLOR_BLACK, FONT_COLOR_GOLD, FONT_COLOR_WHITE


class CreatureRarity:
    def __init__(self, name:str, color: discord.Color, emojii: str, font_color, outline_color):
        self.name = name
        self.color = color
        self.emojii = emojii
        self.font_color = font_color
        self.outline_color = outline_color


# Define global rarity constants
COMMON = CreatureRarity(name="Common", color=discord.Color.light_gray(), emojii='⬜',font_color=FONT_COLOR_WHITE, outline_color=FONT_COLOR_BLACK)
UNCOMMON = CreatureRarity(name="Uncommon", color=discord.Color.green(), emojii='🟩', font_color=(87, 242, 135), outline_color=FONT_COLOR_BLACK)
RARE = CreatureRarity(name="Rare", color=discord.Color.blue(), emojii='🟦', font_color=(52, 152, 219), outline_color=FONT_COLOR_BLACK)
EPIC = CreatureRarity(name="Epic", color=discord.Color.purple(), emojii='🟪', font_color=(155, 89, 182), outline_color=FONT_COLOR_BLACK)
LEGENDARY = CreatureRarity(name="Legendary", color=discord.Color.yellow(), emojii='🟨', font_color=(250, 204, 20), outline_color=FONT_COLOR_BLACK)
MYTHICAL = CreatureRarity(name="Mythical", color=discord.Color.gold(), emojii='⭐', font_color=(255, 215, 0), outline_color=(235, 233, 210))
TRANSCENDANT = CreatureRarity(name="Transcendant", color=discord.Color.red(), emojii='⁉️', font_color=FONT_COLOR_BLACK, outline_color=(255, 0, 0))

NORMAL = CreatureRarity(name="Normal", color=discord.Color(0xFFFFFF)  , emojii='⚪️', font_color=FONT_COLOR_WHITE, outline_color=FONT_COLOR_BLACK)
EXOTIC = CreatureRarity(name="Exotic", color=discord.Color.teal(), emojii='💎️', font_color=(255, 215, 0), outline_color=FONT_COLOR_BLACK)
OMNIPOTENT = CreatureRarity(name="Omnipotent", color=discord.Color.pink(), emojii='🌈', font_color=(255, 215, 0), outline_color=FONT_COLOR_BLACK)

# List of all rarities for easy iteration
ALL_RARITIES = [COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHICAL, TRANSCENDANT]


def get_rarity_by_name(name: str):
    for rarity in ALL_RARITIES:
        if rarity.name.lower() == name.lower():
            return rarity
    return None

def get_rarity():
    roll = random.randint(1, 10000)
    # Select rarity based on defined probabilities
    if roll <= 33:  # 0.33% chance for LEGENDARY
        selected_rarity = LEGENDARY
    elif roll <= 133:  # 1% chance for EPIC (rolls 34-133)
        selected_rarity = EPIC
    elif roll <= 533:  # 4% chance for RARE (rolls 134-533)
        selected_rarity = RARE
    elif roll <= 3833:  # 33% chance for UNCOMMON (rolls 534-3833)
        selected_rarity = UNCOMMON
    else:  # 61.67% chance for COMMON (rolls 3834-10000)
        selected_rarity = COMMON

    return selected_rarity