import discord
from discord.ui import Button

from src.commons.CommonFunctions import interaction_guard, pad_text
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.resources.constants.TGO_MMO_constants import TGOMMO_RARITY_MYTHICAL


#************************************************************************************
#-------------------------------------------BUTTONS---------------------------------------------
#************************************************************************************
# Placeholder button that does nothing when clicked
def create_dummy_label_button(label_text, row=1):
    button = Button(label=f"{label_text}", style=discord.ButtonStyle.gray, row=row)
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
    button = Button(label="\u200b",   style=discord.ButtonStyle.gray, disabled=True, row=row)
    button.callback = dummy_callback()
    return button

# Creates a series of messages showing a player all of their caught creatures with IDs & nicknames
def create_display_creature_collection_button(user, row=0):
    button = Button(label="See Creature Storage", style=discord.ButtonStyle.red, row=row)
    button.callback = display_creature_collection_callback(user)
    return button

def display_creature_collection_callback(user):
    async def callback(interaction):
        user_creature_collection = get_tgommo_db_handler().get_user_creatures_by_user_id(user_id=user.user_id)

        page_num = 0
        pages = [f"Total Unique Creatures Caught: {len(user_creature_collection)}"]
        ordered_creatures = sorted(user_creature_collection, key=lambda c: c.dex_no)

        for creature_index, creature in enumerate(ordered_creatures):
            current_page = pages[page_num]

            creature_name = f'{creature.name}{f" -  {creature.variant_name}" if creature.variant_name != "" else ""}'
            emojiis = f"{'✨' if creature.local_rarity.name == TGOMMO_RARITY_MYTHICAL else ''}{'💖' if creature.is_favorite else ''}{'❗' if creature.nickname else ''}"
            nickname = f"**__{creature.nickname}__**" if creature.nickname != '' else creature.name

            newlines = f'{"\n" if creature.creature_id != ordered_creatures[creature_index - 1].creature_id else ""}\n'
            new_entry = f"{newlines}{creature_index + 1}.  \t\t [{creature.catch_id}] \t ({pad_text(creature_name, 20)}) \t {pad_text(f'{emojiis}{nickname}', 20)}"

            if len(current_page) + len(new_entry) > 1900:
                page_num += 1
                pages.append('')

            pages[page_num] += new_entry

        text = f"\n# {user.nickname}'s Creature Collection (1/{len(pages)}):\n{pages[0]}"
        await interaction.response.send_message(text, ephemeral=True)

        for page_index, page in enumerate(pages):
            if page_index == 0:
                continue
            text = f"\n# {user.nickname}'s Creature Collection ({page_index + 1}/{len(pages)}):\n{page}"
            await interaction.followup.send(text, ephemeral=True)
    return callback