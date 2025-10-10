import datetime
from fileinput import filename

import discord
import pytz
from sqlalchemy.util import await_only

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.resources.constants.file_paths import IMAGE_FOLDER_CREATURES_PATH, PLAYER_PROFILE_AVATAR_BASE, \
    IMAGE_FILE_EXTENSION


class AvatarUnlockHandler:
    def __init__(self, user_id, nickname=None, interaction=None):
        self.user_id = user_id
        self.nickname = nickname
        self.interaction = interaction

    async def check_avatar_unlock_conditions(self):
        # secret unlocks
        if self.nickname:
            await self.handle_nickname_based_unlocks()

        # event unlocks
        self.handle_avatar_pim_unlock()
        await self.handle_avatar_charlie_unlock()
        await self.handle_avatar_freddy_unlock()

        #quests unlocks


    async def handle_nickname_based_unlocks(self):
        unlocked_secret_avatars = get_tgommo_db_handler().get_unlocked_avatar_ids_for_server()
        player = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=self.user_id, convert_to_object=True)

        avatar_combos = {
            "jordo": ("S1", "_Secret_1_Jordo"),
            "miku": ("S2", "_Secret_2_Miku"),
            "garfield": ("S3", "_Secret_3_Garfield"),
            "samus": ("S4", "_Secret_4_Samus"),
            "boss baby": ("S5", "_Secret_5_BossBaby"),
            "walter white": ("S6", "_Secret_6_WalterWhite"),
        }

        if self.nickname is not None and self.nickname.lower() in avatar_combos:
            avatar_id = avatar_combos[self.nickname.lower()][0]
            file_name = avatar_combos[self.nickname.lower()][1]

            if avatar_id not in unlocked_secret_avatars:
                get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=avatar_id, user_id=-1)
                await self.interaction.channel.send(f"The secret avatar *{self.nickname.upper()}* has been unlocked for the server thanks to @{player.nickname}!!", file=discord.File(f"{PLAYER_PROFILE_AVATAR_BASE}{file_name}{IMAGE_FILE_EXTENSION}", filename="avatar.png"))
            return

    # event unlock handlers
    def handle_avatar_pim_unlock(self):
        user_ids_who_played_beta = get_tgommo_db_handler().get_users_who_played_during_time_range(max_timestamp='2025-10-07 00:00:00')
        for user_id in user_ids_who_played_beta:
            get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id="E1", user_id=user_id)

    async def handle_avatar_charlie_unlock(self):
        current_time = datetime.datetime.now(pytz.UTC)
        is_within_opening_week = (datetime.datetime(2025, 9, 10, 12, 0, 0, tzinfo=pytz.UTC) <= current_time <= datetime.datetime(2025, 10, 17, 23, 59, 59, tzinfo=pytz.UTC))

        if is_within_opening_week and not get_tgommo_db_handler().check_if_user_unlocked_avatar(avatar_id="E2", user_id=self.user_id):
            get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id="E2", user_id=self.user_id)

            avatar_path = f"{PLAYER_PROFILE_AVATAR_BASE}_Event_2_Charlie{IMAGE_FILE_EXTENSION}"
            await self.interaction.followup.send(f"You have unlocked the special opening week avatar: Charlie!", file=discord.File(avatar_path, filename="avatar.png"), ephemeral=True)

    async def handle_avatar_freddy_unlock(self):
        current_time = datetime.datetime.now(pytz.UTC)
        is_halloween_2025 = (current_time.year == 2025 and current_time.month == 10 and current_time.day == 31)

        if is_halloween_2025 and not get_tgommo_db_handler().check_if_user_unlocked_avatar(avatar_id="E3", user_id=self.user_id):
            get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id="E3", user_id=self.user_id)

            avatar_path = f"{PLAYER_PROFILE_AVATAR_BASE}_Event_3_Freddy{IMAGE_FILE_EXTENSION}"
            await self.interaction.followup.send(f"You have unlocked the special halloween 2025 avatar: Freddy Fazbear!", file=discord.File(avatar_path, filename="avatar.png"), ephemeral=True)
