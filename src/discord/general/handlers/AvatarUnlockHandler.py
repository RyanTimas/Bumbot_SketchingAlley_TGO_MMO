import datetime

import discord
import pytz

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.file_paths import *


class AvatarUnlockHandler:
    def __init__(self, user_id, nickname=None, interaction=None):
        self.user_id = user_id
        self.nickname = nickname
        self.interaction = interaction

    async def check_avatar_unlock_conditions(self, creature:TGOCreature =None):
        # secret unlocks
        if self.nickname:
            await self.handle_nickname_based_unlocks()

        # quests unlocks
        await self.define_avatar_quests_unlocks()

        # event unlocks
        await self.timeline_based_avatar_unlocks()

        # todo: handle special case unlocks based on creature caught
        if creature:
            pass


    # NICKNAME-BASED UNLOCK HANDLERS
    async def handle_nickname_based_unlocks(self):
        unlocked_secret_avatars = get_tgommo_db_handler().get_unlocked_avatar_ids_for_server()
        player = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=self.user_id, convert_to_object=True)

        avatar_combos = {
            # WAVE 1
            (("jordo",), ("Jordo", "S1", "Jordo")),
            (("miku",), ("Hatsune Miku", "S2", "Miku")),
            (("garfield",), ("Garfield", "S3", "Garfield")),
            (("samus", "aran", "metroid"),  ("Samus Aran", "S4", "Samus")),
            (("boss", "baby"), ("the Boss Baby", "S5", "BossBaby")),
            (("white", "walter"), ("Walter White", "S6", "WalterWhite")),
            # WAVE 2
            (("pink", "jesse"), ("Jesse Pinkman", "S7", "JessePinkman")),
            (("mike", "ehrmantraut", "finger"), ("Mike Ehrmantraut", "S8", "MikeEhrmantraut")),
            (("porky", "pig"), ("Porky Pig", "S9", "Porky")),
        }

        for avatar in avatar_combos:
            unlock_terms = avatar[0]
            avatar_name = avatar[1][0]
            avatar_id = avatar[1][1]
            avatar_img_root = avatar[1][2]

            for unlock_term in unlock_terms:
                if unlock_term in self.nickname.lower():
                    file_name = f"_Secret_{avatar_img_root}"

                    if avatar_id not in unlocked_secret_avatars:
                        get_tgommo_db_handler().unlock_avatar_for_server(avatar_id=avatar_id)
                        await self.interaction.channel.send(f"The secret avatar *{avatar_name}* has been unlocked for the server thanks to @{player.nickname}!!", file=discord.File(f"{PLAYER_PROFILE_AVATAR_BASE}{file_name}{IMAGE_FILE_EXTENSION}", filename="avatar.png"))
                    return

    # EVENT-BASED UNLOCK HANDLERS
    async  def timeline_based_avatar_unlocks(self):
        timeline_params = [
            ("Freddy Fazbear", "3", datetime.datetime(2025, 10, 31, 0, 0, 1, tzinfo=pytz.UTC), datetime.datetime(2025, 10, 31, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),

            ("Charlie", "2", datetime.datetime(2025, 9, 10, 12, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 10, 16, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Allan", "4", datetime.datetime(2025, 10, 17, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 10, 23, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Glep", "5", datetime.datetime(2025, 10, 24, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 10, 30, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("The Boss", "6", datetime.datetime(2025, 10, 31, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 11, 6, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Mr Frog", "7", datetime.datetime(2025, 11, 7, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 11, 13, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Tyler", "8", datetime.datetime(2025, 11, 14, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 11, 20, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Smormu", "9", datetime.datetime(2025, 11, 21, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 11, 27, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
        ]

        for timeline_param in timeline_params:
            name = timeline_param[0]
            avatar_id = timeline_param[1]
            start_time = timeline_param[2]
            end_time = timeline_param[3]
            user_id = timeline_param[4]

            current_time = datetime.datetime.now(pytz.UTC)
            if start_time <= current_time <= end_time and not get_tgommo_db_handler().check_if_user_unlocked_avatar(avatar_id=f"E{avatar_id}", user_id=self.user_id):
                get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=f"E{avatar_id}", user_id=self.user_id)

                avatar_path = f"{PLAYER_PROFILE_AVATAR_BASE}_Event_{name.replace(' ', '')}{IMAGE_FILE_EXTENSION}"
                await self.interaction.followup.send(f"You have unlocked the special limited time avatar: {name}!", file=discord.File(avatar_path, filename="avatar.png"), ephemeral=True)


    # QUEST-BASED UNLOCK HANDLERS
    async def define_avatar_quests_unlocks(self):
        unlockable_avatars = get_tgommo_db_handler().get_avatar_unlock_conditions(convert_to_object=True)

        for unlockable_avatar in unlockable_avatars:
            params = (self.user_id,)
            await self.handle_quest_complete_check(avatar= unlockable_avatar, params=params,)

    async  def handle_quest_complete_check(self, avatar, params):
        user_reached_threshold = get_tgommo_db_handler().QueryHandler.execute_query(query=avatar.unlock_query, params=params)[0][0] >= avatar.unlock_threshold

        if user_reached_threshold:
            # if quest rewards more than one avatar (parent entry), unlock all child avatars
            avatars_to_unlock = [avatar] if not avatar.is_parent_entry else get_tgommo_db_handler().get_child_avatars_by_parent_id(parent_avatar_id=avatar.avatar_id, convert_to_object=True)

            for child_avatar in avatars_to_unlock:
                if get_tgommo_db_handler().check_if_user_unlocked_avatar(avatar_id=child_avatar.avatar_id, user_id=self.user_id):
                    continue

                get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=child_avatar.avatar_id, user_id=self.user_id)
                avatar_path = f"{PLAYER_PROFILE_AVATAR_BASE}_Quest_{child_avatar.img_root}{IMAGE_FILE_EXTENSION}"
                await self.interaction.followup.send(f"You have completed a quest & unlocked the avatar: {child_avatar.name}!!", file=discord.File(avatar_path, filename="avatar.png"), ephemeral=True)