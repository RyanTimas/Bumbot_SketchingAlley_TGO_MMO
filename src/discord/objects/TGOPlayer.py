from src.discord.objects.TGOAvatar import TGOAvatar


class TGOPlayer:
    def __init__(self, player_id:int, user_id: int, nickname:str, avatar:TGOAvatar, background_id:int, creature_slot_id_1:int, creature_slot_id_2:int, creature_slot_id_3:int, creature_slot_id_4:int, creature_slot_id_5:int, creature_slot_id_6:int, currency:int, available_catches:int, rod_level:int, rod_amount:int, trap_level:int, trap_amount:int):
        self.player_id = player_id
        self.user_id = user_id

        self.nickname = nickname
        self.avatar = avatar
        self.background_id = background_id

        self.creature_slot_id_1 = creature_slot_id_1
        self.creature_slot_id_2 = creature_slot_id_2
        self.creature_slot_id_3 = creature_slot_id_3
        self.creature_slot_id_4 = creature_slot_id_4
        self.creature_slot_id_5 = creature_slot_id_5
        self.creature_slot_id_6 = creature_slot_id_6

        self.currency = currency
        self.available_catches = available_catches
        self.rod_level = rod_level
        self.rod_amount = rod_amount
        self.trap_level = trap_level
        self.trap_amount = trap_amount