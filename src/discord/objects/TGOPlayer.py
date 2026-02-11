from src.commons.GuildHandler import get_guild
from src.discord.objects.TGOAvatar import TGOAvatar
from src.discord.objects.TGOCreature import PLACEHOLDER_CREATURE


class TGOPlayer:
    def __init__(
        self,
        player_id:int, user_id: int,
        nickname:str,
        avatar:TGOAvatar, background_id:int,
        creature_slot_id_1:int, creature_slot_id_2:int, creature_slot_id_3:int, creature_slot_id_4:int, creature_slot_id_5:int, creature_slot_id_6:int,
        currency:int,
        available_catch_attempts:int,
        rod_level:int, rod_amount:int, trap_level:int, trap_amount:int
    ):
        self.player_id = player_id
        self.user_id = user_id

        self.nickname = nickname
        self.avatar = avatar
        self.background_id = background_id

        # todo: see if we can remove these
        self.creature_slot_id_1 = creature_slot_id_1
        self.creature_slot_id_2 = creature_slot_id_2
        self.creature_slot_id_3 = creature_slot_id_3
        self.creature_slot_id_4 = creature_slot_id_4
        self.creature_slot_id_5 = creature_slot_id_5
        self.creature_slot_id_6 = creature_slot_id_6

        self.currency = currency
        self.available_catches = available_catch_attempts
        self.rod_level = rod_level
        self.rod_amount = rod_amount
        self.trap_level = trap_level
        self.trap_amount = trap_amount

        # additonal fields that are not stored in the database, but are useful for the discord bot to have easy access to
        self.display_creatures = self.define_user_display_creatures()
        self.discord_profile = get_guild().get_member(self.user_id)


    def define_user_display_creatures(self):
        from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
        return [
            get_tgommo_db_handler().get_user_creature_by_catch_id(catch_id=self.creature_slot_id_1) if self.creature_slot_id_1 != -1 else PLACEHOLDER_CREATURE,
            get_tgommo_db_handler().get_user_creature_by_catch_id(catch_id=self.creature_slot_id_2) if self.creature_slot_id_2 != -1 else PLACEHOLDER_CREATURE,
            get_tgommo_db_handler().get_user_creature_by_catch_id(catch_id=self.creature_slot_id_3) if self.creature_slot_id_3 != -1 else PLACEHOLDER_CREATURE,
            get_tgommo_db_handler().get_user_creature_by_catch_id(catch_id=self.creature_slot_id_4) if self.creature_slot_id_4 != -1 else PLACEHOLDER_CREATURE,
            get_tgommo_db_handler().get_user_creature_by_catch_id(catch_id=self.creature_slot_id_5) if self.creature_slot_id_5 != -1 else PLACEHOLDER_CREATURE,
            get_tgommo_db_handler().get_user_creature_by_catch_id(catch_id=self.creature_slot_id_6) if self.creature_slot_id_6 != -1 else PLACEHOLDER_CREATURE
        ]