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
COMMON = CreatureRarity(name="Common", color=discord.Color.light_gray(), emojii='⬜',font_color=(153, 170, 181), outline_color=FONT_COLOR_BLACK)
UNCOMMON = CreatureRarity(name="Uncommon", color=discord.Color.green(), emojii='🟩', font_color=(67, 181, 129), outline_color=FONT_COLOR_WHITE)
RARE = CreatureRarity(name="Rare", color=discord.Color.blue(), emojii='🟦', font_color=(88, 101, 242), outline_color=FONT_COLOR_BLACK)
EPIC = CreatureRarity(name="Epic", color=discord.Color.purple(), emojii='🟪', font_color=(114, 137, 218), outline_color=FONT_COLOR_WHITE)
LEGENDARY = CreatureRarity(name="Legendary", color=discord.Color.yellow(), emojii='🟨', font_color=(250, 204, 20), outline_color=FONT_COLOR_GOLD)
MYTHICAL = CreatureRarity(name="Mythical", color=discord.Color.gold(), emojii='⭐', font_color=(255, 215, 0), outline_color=(235, 233, 210))

# List of all rarities for easy iteration
ALL_RARITIES = [COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHICAL]


def get_rarity_by_name(name: str):
    for rarity in ALL_RARITIES:
        if rarity.name.lower() == name.lower():
            return rarity
    return None

def get_rarity():
    roll = random.randint(1, 100)
    # Select rarity based on defined probabilities
    if roll <= 1:  # 1% chance
        selected_rarity = LEGENDARY
    elif roll <= 6:  # 5% chance (rolls 2-6)
        selected_rarity = EPIC
    elif roll <= 21:  # 15% chance (rolls 7-21)
        selected_rarity = RARE
    elif roll <= 46:  # 25% chance (rolls 22-46)
        selected_rarity = UNCOMMON
    else:  # 54% chance (rolls 47-100)
        selected_rarity = COMMON

    return selected_rarity