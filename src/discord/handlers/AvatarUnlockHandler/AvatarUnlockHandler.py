import datetime

import discord
import pytz

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.file_paths import *

# todo: separate this into three classes: one for event based unlocks and one for nicknames and one for quests
class AvatarUnlockHandler:
    def __init__(self, user_id, nickname=None, interaction=None):
        self.user_id = user_id
        self.nickname = nickname
        self.interaction = interaction

    async def check_avatar_unlock_conditions(self, creature:TGOCreature =None):
        await self.quest_avatar_unlock_handler()
        await self.limited_time_avatar_unlock_handler()

        # todo: handle special case unlocks based on creature caught
        if creature:
            pass

    # Avatar Type Unlock Handlers
    async def nickname_avatar_unlock_handler(self):
        unlocked_avatars = get_tgommo_db_handler().get_avatars_by_nickname(nickname=self.nickname.lower())
        if unlocked_avatars:
            player = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=self.user_id)
            for avatar in unlocked_avatars:
                get_tgommo_db_handler().unlock_avatar_for_server(avatar_id=avatar.avatar_id)
                await self.interaction.channel.send(f"The secret avatar *{avatar.name}* has been unlocked for the server thanks to @{player.nickname}!!", file=convert_to_png(image=avatar.avatar_unlock_image, file_name="avatar.png"))
    async  def limited_time_avatar_unlock_handler(self):
        # grab a list of all currently active limited time avatars and check if user has unlocked them already, if not unlock them and send message
        unlocked_avatar_ids = [avatar.avatar_id for avatar in get_tgommo_db_handler().get_unlocked_avatars_by_user_id(user_id=self.user_id)]
        active_avatars = [avatar for avatar in get_tgommo_db_handler().get_all_currently_available_limited_time_avatars() if avatar.avatar_id not in unlocked_avatar_ids]
        if not active_avatars:
            return

        for avatar in active_avatars:
            get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=avatar.avatar_id, user_id=self.user_id)
            await self.interaction.followup.send(f"You have unlocked the special limited time avatar: {avatar.name}!", file=convert_to_png(image=avatar.avatar_unlock_image, file_name="avatar.png"), ephemeral=True)
    async  def quest_avatar_unlock_handler(self):
        unlockable_avatars = get_tgommo_db_handler().get_avatars_with_unlock_conditions()
        for unlockable_avatar in unlockable_avatars:
            user_reached_threshold = get_tgommo_db_handler().QueryHandler.execute_query(query=unlockable_avatar.unlock_query, params=(self.user_id,))[0][0] >= unlockable_avatar.unlock_threshold

            if user_reached_threshold:
                # if quest rewards more than one avatar (parent entry), unlock all child avatars
                avatars_to_unlock = [unlockable_avatar] if not unlockable_avatar.is_parent_entry else get_tgommo_db_handler().get_child_avatars_by_parent_id(parent_avatar_id=unlockable_avatar.avatar_id)
                for child_avatar in avatars_to_unlock:
                    if not get_tgommo_db_handler().check_if_user_unlocked_avatar(avatar_id=child_avatar.avatar_id, user_id=self.user_id):
                        get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=child_avatar.avatar_id, user_id=self.user_id)
                        await self.interaction.followup.send(f"You have completed a quest & unlocked the avatar: {child_avatar.name}!!", file=convert_to_png(child_avatar.avatar_unlock_image, file_name="avatar.png"), ephemeral=True)

