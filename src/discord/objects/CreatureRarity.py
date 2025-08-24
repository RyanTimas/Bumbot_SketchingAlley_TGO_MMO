import random

import discord



class CreatureRarity:
    def __init__(self, name:str, color: discord.Color, emojii: str):
        self.name = name
        self.color = color
        self.emojii = emojii


# Define global rarity constants
COMMON = CreatureRarity(name="Common", color=discord.Color.light_gray(), emojii='⬜')
UNCOMMON = CreatureRarity(name="Uncommon", color=discord.Color.green(), emojii='🟩')
RARE = CreatureRarity(name="Rare", color=discord.Color.blue(), emojii='🟦')
EPIC = CreatureRarity(name="Epic", color=discord.Color.purple(), emojii='🟪')
LEGENDARY = CreatureRarity(name="Legendary", color=discord.Color.yellow(), emojii='🟨')
MYTHICAL = CreatureRarity(name="Mythical", color=discord.Color.gold(), emojii='⭐')

# List of all rarities for easy iteration
ALL_RARITIES = [COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHICAL]


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