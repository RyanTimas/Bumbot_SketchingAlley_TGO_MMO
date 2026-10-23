from src.caching import resolve_static_content_cache
from src.caching.db_specific_caches.avatar_cache import AvatarCache
from src.caching.db_specific_caches.quest_collection_cache import QuestCollectionCache
from src.commons.AsyncBlocking import run_serialized_blocking
from src.commons.CommonFunctions import convert_to_png, convert_to_datetime
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature


# check if player has unlocked any secret avatars based on their creature nicknames and unlock them if they haven't already been unlocked
async def check_for_secret_avatars(user_id, interaction, nickname):
    unlocked_avatars = resolve_static_content_cache(QuestCollectionCache).get_avatars_by_nickname(exclude_unlocked_avatars=True, nickname=nickname.lower())
    if unlocked_avatars:
        player = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=user_id)
        for avatar in unlocked_avatars:
            get_tgommo_db_handler().unlock_avatar_for_server(avatar_id=avatar.avatar_id)
            await interaction.channel.send(f"The secret avatar *{avatar.name}* has been unlocked for the server thanks to @{player.nickname}!!", file=convert_to_png(image=avatar.avatar_unlock_image, file_name="avatar.png"))

# check if player has unlocked any limited time event avatars and unlock them if they haven't already been unlocked
async def check_for_event_avatars(user_id, interaction):
    notifications = await run_serialized_blocking(_prepare_event_avatar_notifications, user_id)
    for message, image in notifications:
        await interaction.followup.send(message, file=image, ephemeral=True)
def _prepare_event_avatar_notifications(user_id):
    unlocked_avatars = get_tgommo_db_handler().get_currently_available_limited_time_avatars(exclude_unlocked_avatars=True, user_id=user_id)
    notifications = []
    for avatar in unlocked_avatars or []:
        get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=avatar.avatar_id, user_id=user_id)
        notifications.append((f"You have unlocked the special limited time avatar: {avatar.name}!", convert_to_png(image=avatar.avatar_unlock_image, file_name="avatar.png"),))
    return notifications

# check if player has unlocked any quest avatars
async def check_for_quest_avatars(user_id, interaction):
    notifications = await run_serialized_blocking(_prepare_quest_avatar_notifications, user_id)
    for message, image in notifications:
        await interaction.followup.send(message, file=image, ephemeral=True)
def _prepare_quest_avatar_notifications(user_id):
    unlockable_avatars = resolve_static_content_cache(QuestCollectionCache).get_avatars_with_unlock_conditions(exclude_unlocked_avatars=True, user_id=user_id)
    if not unlockable_avatars:
        return []

    # Execute unlock queries in the DB for each avatar and check if the unlock threshold is met
    unlock_results = []
    for avatar in unlockable_avatars:
        try:
            result = get_tgommo_db_handler().QueryHandler.execute_query(query=avatar.unlock_query, params=(user_id,))[0][0]
            unlock_results.append((avatar, result >= avatar.unlock_threshold))
        except Exception:
            unlock_results.append((avatar, False))

    # Filter avatars that meet the unlock threshold and handle parent-child relationships, then check if they are already unlocked
    avatars_to_process = []
    for avatar, threshold_met in unlock_results:
        if threshold_met:
            if avatar.is_parent_entry:
                avatars_to_process.extend(resolve_static_content_cache(AvatarCache).get_child_avatars_by_parent_id(parent_avatar_id=avatar.avatar_id))
            else:
                avatars_to_process.append(avatar)
    if not avatars_to_process:
        return []

    avatar_ids = [avatar.avatar_id for avatar in avatars_to_process]
    already_unlocked = get_tgommo_db_handler().batch_check_unlocked_avatars(avatar_ids=avatar_ids, user_id=user_id)
    new_unlocks = [avatar for avatar in avatars_to_process if avatar.avatar_id not in already_unlocked]
    if new_unlocks:
        get_tgommo_db_handler().batch_insert_avatar_links(avatars=new_unlocks, user_id=user_id)

    # Prepare notifications for newly unlocked avatars
    return [(f"You have completed a quest & unlocked the avatar: {avatar.name}!!", convert_to_png(avatar.avatar_unlock_image, file_name="avatar.png"),) for avatar in new_unlocks]

# check if player has unlocked any special quest avatars based on the time difference between the creature's spawn and catch times
async def check_for_special_quest_avatars(user_id, creature: TGOCreature, interaction):
    notification = await run_serialized_blocking(_prepare_special_quest_notification, user_id, creature)
    if notification:
        message, image = notification
        await interaction.followup.send(message, file=image, ephemeral=True)
def _prepare_special_quest_notification(user_id, creature: TGOCreature):
    # TURBO GRANNY AVATAR UNLOCK CONDITION: If the player catches a creature within 3 seconds of its spawn time, they unlock the Turbo Granny avatar.
    if abs((convert_to_datetime(creature.catch_time) - convert_to_datetime(creature.spawn_time)).total_seconds()) < 3.0:
        turbo_granny_avatar = resolve_static_content_cache(AvatarCache).get_avatar_by_id(avatar_id="Q9")
        get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=turbo_granny_avatar.avatar_id, user_id=user_id)
        return f"You have completed a special quest & unlocked the avatar: {turbo_granny_avatar.name}!!", convert_to_png(turbo_granny_avatar.avatar_unlock_image, file_name="avatar.png"),
    return None
