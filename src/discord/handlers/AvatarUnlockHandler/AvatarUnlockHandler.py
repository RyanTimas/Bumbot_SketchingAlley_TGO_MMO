import datetime

import discord
import pytz

from src.commons.CommonFunctions import convert_to_png, convert_to_datetime
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.file_paths import *

# check if player has unlocked any secret avatars based on their creature nicknames and unlock them if they haven't already been unlocked
async def check_for_secret_avatars(user_id, interaction, nickname):
    unlocked_avatars = get_tgommo_db_handler().get_avatars_by_nickname(exclude_unlocked_avatars=True, nickname=nickname.lower())
    if unlocked_avatars:
        player = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=user_id)
        for avatar in unlocked_avatars:
            get_tgommo_db_handler().unlock_avatar_for_server(avatar_id=avatar.avatar_id)
            await interaction.channel.send(f"The secret avatar *{avatar.name}* has been unlocked for the server thanks to @{player.nickname}!!", file=convert_to_png(image=avatar.avatar_unlock_image, file_name="avatar.png"))
# check if player has unlocked any limited time event avatars and unlock them if they haven't already been unlocked
async def check_for_event_avatars(user_id, interaction):
    unlocked_avatars = get_tgommo_db_handler().get_currently_available_limited_time_avatars(exclude_unlocked_avatars=True, user_id=user_id)
    if not unlocked_avatars:
        return

    for avatar in unlocked_avatars:
        get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=avatar.avatar_id, user_id=user_id)
        await interaction.followup.send(f"You have unlocked the special limited time avatar: {avatar.name}!", file=convert_to_png(image=avatar.avatar_unlock_image, file_name="avatar.png"), ephemeral=True)
# check if player has unlocked any quest avatars
async def check_for_quest_avatars(user_id, interaction):
    unlockable_avatars = get_tgommo_db_handler().get_avatars_with_unlock_conditions(exclude_unlocked_avatars=True, user_id=user_id)
    if not unlockable_avatars:
        return

    # Batch execute all unlock queries at once
    unlock_results = []
    for avatar in unlockable_avatars:
        try:
            result = get_tgommo_db_handler().QueryHandler.execute_query(query=avatar.unlock_query, params=(user_id,))[0][0]
            unlock_results.append((avatar, result >= avatar.unlock_threshold))
        except Exception:
            unlock_results.append((avatar, False))

        # Collect all avatars that need unlocking
        avatars_to_process = []
        for avatar, threshold_met in unlock_results:
            if threshold_met:
                if avatar.is_parent_entry:
                    child_avatars = get_tgommo_db_handler().get_child_avatars_by_parent_id(parent_avatar_id=avatar.avatar_id)
                    avatars_to_process.extend(child_avatars)
                else:
                    avatars_to_process.append(avatar)

        if not avatars_to_process:
            return

        # Batch check which avatars are already unlocked
        avatar_ids = [avatar.avatar_id for avatar in avatars_to_process]
        already_unlocked = get_tgommo_db_handler().batch_check_unlocked_avatars(avatar_ids=avatar_ids, user_id=user_id)

        # Batch insert new avatar unlocks
        new_unlocks = [avatar for avatar in avatars_to_process if avatar.avatar_id not in already_unlocked]
        if new_unlocks:
            get_tgommo_db_handler().batch_insert_avatar_links(avatars=new_unlocks, user_id=user_id)

            # Send notifications for newly unlocked avatars
            for avatar in new_unlocks:
                await interaction.followup.send(f"You have completed a quest & unlocked the avatar: {avatar.name}!!", file=convert_to_png(avatar.avatar_unlock_image, file_name="avatar.png"), ephemeral=True)

async def check_for_special_quest_avatars(user_id, creature: TGOCreature, interaction):
    catch_dt = convert_to_datetime(creature.catch_time)
    spawn_dt = convert_to_datetime(creature.spawn_time)
    diff_seconds = abs((catch_dt - spawn_dt).total_seconds())
    print(f"Spawn time: {spawn_dt}, Catch time: {catch_dt}")
    print(f"Time taken to catch creature: {diff_seconds} seconds")

    if diff_seconds < 3.0:
        print("good job")
        turbo_granny_avatar = get_tgommo_db_handler().get_avatar_by_id(avatar_id='Q9')
        await interaction.followup.send(f"You have completed a special quest & unlocked the avatar: {turbo_granny_avatar.name}!!", file=convert_to_png(turbo_granny_avatar.avatar_unlock_image, file_name="avatar.png"), ephemeral=True)
        get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=turbo_granny_avatar.avatar_id, user_id=user_id)


