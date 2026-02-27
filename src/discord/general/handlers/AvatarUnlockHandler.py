import datetime

import discord
import pytz

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.file_paths import *


class AvatarUnlockHandler:
    def __init__(self, user_id, nickname=None, interaction=None):
        self.user_id = user_id
        self.nickname = nickname
        self.interaction = interaction

    async def check_avatar_unlock_conditions(self, creature:TGOCreature =None):
        if self.nickname:
            await self.nickname_avatar_unlock_handler()
        await self.quest_avatar_unlock_handler()
        await self.limited_time_avatar_unlock_handler()

        # todo: handle special case unlocks based on creature caught
        if creature:
            pass


    async def nickname_avatar_unlock_handler(self):
        unlocked_secret_avatars = get_tgommo_db_handler().get_unlocked_avatars_for_server()
        player = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=self.user_id)

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
            (("jason", "vorhees", "13"), ("Jason Vorhees", "S10", "JasonVorhees")),
        }

        for avatar in avatar_combos:
            unlock_terms = avatar[0]
            avatar = get_tgommo_db_handler().get_avatar_by_id(avatar_id=avatar[1][1])

            for unlock_term in unlock_terms:
                if unlock_term in self.nickname.lower():
                    if not any(avatar.avatar_id == secret_avatar.avatar_id for secret_avatar in unlocked_secret_avatars):
                        get_tgommo_db_handler().unlock_avatar_for_server(avatar_id=avatar.avatar_id)
                        await self.interaction.channel.send(f"The secret avatar *{avatar.name}* has been unlocked for the server thanks to @{player.nickname}!!", file=convert_to_png(image=avatar.avatar_image, file_name="avatar.png"))
                    return
    async  def limited_time_avatar_unlock_handler(self):
        timeline_params = [
            # Holidays
            ("Freddy Fazbear", "3", datetime.datetime(2025, 10, 31, 0, 0, 1, tzinfo=pytz.UTC), datetime.datetime(2025, 10, 31, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),

            # Wave 1
            ("Charlie", "2", datetime.datetime(2025, 9, 10, 12, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 10, 16, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Allan", "4", datetime.datetime(2025, 10, 17, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 10, 23, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Glep", "5", datetime.datetime(2025, 10, 24, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 10, 30, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("The Boss", "6", datetime.datetime(2025, 10, 31, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 11, 6, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Mr Frog", "7", datetime.datetime(2025, 11, 7, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 11, 13, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Tyler", "8", datetime.datetime(2025, 11, 14, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 11, 20, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Smormu", "9", datetime.datetime(2025, 11, 21, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 11, 27, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Blue Janitor Dude", "10", datetime.datetime(2025, 11, 28, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 12, 4, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Dolly Dimpley", "11", datetime.datetime(2025, 12, 5, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 12, 11, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Cool Autistic Gamer 774", "12", datetime.datetime(2025, 12, 12, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2025, 12, 18, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),

            # Wave 2
            ("Yuji Itadori", "13", datetime.datetime(2026, 1, 15, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 1, 22, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Megumi Fushiguro", "14", datetime.datetime(2026, 1, 15, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 1, 22, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Nobara Kugisaki", "15", datetime.datetime(2026, 1, 15, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 1, 22, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Satoru Gojo", "16", datetime.datetime(2026, 1, 22, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 1, 29, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Kento Nanami", "17", datetime.datetime(2026, 1, 29, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 2, 5, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Maki Zen'in", "18", datetime.datetime(2026, 2, 5, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 2, 12, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Suguru Geto", "19", datetime.datetime(2026, 2, 12, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 3, 26, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Toji Fushiguro", "20", datetime.datetime(2026, 2, 19, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 3, 26, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Mahito", "21", datetime.datetime(2026, 2, 26, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 3, 26, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Panda", "22", datetime.datetime(2026, 3, 5, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 3, 26, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Jogo", "23", datetime.datetime(2026, 3, 12, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 3, 26, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
            ("Ryomen Sukuna", "24", datetime.datetime(2026, 3, 19, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime(2026, 3, 26, 23, 59, 59, tzinfo=pytz.UTC), (self.user_id,)),
        ]

        for timeline_param in timeline_params:
            avatar_id = f"E{timeline_param[1]}"
            start_time = timeline_param[2]
            end_time = timeline_param[3]

            current_time = datetime.datetime.now(pytz.UTC)
            if start_time <= current_time <= end_time and not get_tgommo_db_handler().check_if_user_unlocked_avatar(avatar_id=avatar_id, user_id=self.user_id):
                get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=avatar_id, user_id=self.user_id)

                avatar = get_tgommo_db_handler().get_avatar_by_id(avatar_id=avatar_id)
                await self.interaction.followup.send(f"You have unlocked the special limited time avatar: {avatar.name}!", file=convert_to_png(image=avatar.avatar_image, file_name="avatar.png"), ephemeral=True)
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
                        await self.interaction.followup.send(f"You have completed a quest & unlocked the avatar: {child_avatar.name}!!", file=convert_to_png(child_avatar.avatar_image, file_name="avatar.png"), ephemeral=True)

