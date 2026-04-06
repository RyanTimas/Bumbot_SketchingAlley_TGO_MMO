import datetime

import discord
import pytz

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.file_paths import *

# check if player has unlocked any secret avatars based on their creature nicknames and unlock them if they haven't already been unlocked
async def check_for_secret_avatars(user_id, interaction, nickname):
    unlocked_avatars = get_tgommo_db_handler().get_avatars_by_nickname(nickname=nickname.lower())
    if unlocked_avatars:
        player = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=user_id)
        for avatar in unlocked_avatars:
            get_tgommo_db_handler().unlock_avatar_for_server(avatar_id=avatar.avatar_id)
            await interaction.channel.send(f"The secret avatar *{avatar.name}* has been unlocked for the server thanks to @{player.nickname}!!", file=convert_to_png(image=avatar.avatar_unlock_image, file_name="avatar.png"))
# check if player has unlocked any limited time event avatars and unlock them if they haven't already been unlocked
async def check_for_event_avatars(user_id, interaction):
    unlocked_avatar_ids = [avatar.avatar_id for avatar in get_tgommo_db_handler().get_unlocked_avatars_by_user_id(user_id=user_id)]
    active_avatars = [avatar for avatar in get_tgommo_db_handler().get_all_currently_available_limited_time_avatars() if avatar.avatar_id not in unlocked_avatar_ids]
    if not active_avatars:
        return

    for avatar in active_avatars:
        get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=avatar.avatar_id, user_id=user_id)
        await interaction.followup.send(f"You have unlocked the special limited time avatar: {avatar.name}!", file=convert_to_png(image=avatar.avatar_unlock_image, file_name="avatar.png"), ephemeral=True)
# check if player has unlocked any quest avatars
async def check_for_quest_avatars(user_id, interaction):
    unlockable_avatars = get_tgommo_db_handler().get_avatars_with_unlock_conditions()
    for unlockable_avatar in unlockable_avatars:
        user_reached_threshold = get_tgommo_db_handler().QueryHandler.execute_query(query=unlockable_avatar.unlock_query, params=(user_id,))[0][0] >= unlockable_avatar.unlock_threshold

        if user_reached_threshold:
            avatars_to_unlock = [unlockable_avatar] if not unlockable_avatar.is_parent_entry else get_tgommo_db_handler().get_child_avatars_by_parent_id(parent_avatar_id=unlockable_avatar.avatar_id)
            for child_avatar in avatars_to_unlock:
                if not get_tgommo_db_handler().check_if_user_unlocked_avatar(avatar_id=child_avatar.avatar_id, user_id=user_id):
                    get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=child_avatar.avatar_id, user_id=user_id)
                    await interaction.followup.send(f"You have completed a quest & unlocked the avatar: {child_avatar.name}!!", file=convert_to_png(child_avatar.avatar_unlock_image, file_name="avatar.png"), ephemeral=True)

