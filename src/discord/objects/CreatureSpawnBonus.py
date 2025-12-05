import datetime
import random

import pytz

from src.discord.objects.CreatureRarity import CreatureRarity


class CreatureSpawnBonus:
    def __init__(self, bonus_type:str, bonus_name:str, rarity: CreatureRarity, spawn_odds:int, image):
        self.bonus_type = bonus_type
        self.bonus_name = bonus_name
        self.rarity = rarity
        self.spawn_odds = spawn_odds
        self.image = image

        self.spawn_time = None
        self.time_to_despawn = 15
        self.despawn_time = None
        self.refresh_spawn_and_despawn_time(timezone=pytz.UTC)

    def refresh_spawn_and_despawn_time(self, timezone):
        self.spawn_time = datetime.datetime.now(pytz.UTC).astimezone(timezone)
        self.despawn_time = self.spawn_time + datetime.timedelta(minutes=self.time_to_despawn)
        self.time_to_despawn = self.time_to_despawn * 60  # convert to seconds