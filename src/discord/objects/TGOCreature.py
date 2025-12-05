import datetime
import pytz
import random
import time

from src.discord.objects.CreatureRarity import COMMON, UNCOMMON, CreatureRarity, RARE, EPIC, LEGENDARY
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.TGO_MMO_creature_constants import *


class TGOCreature:
    def __init__(self, creature_id: int, name:str, variant_name:str, dex_no: int, variant_no: int, full_name: str, scientific_name: str, kingdom: str, description: str, img_root: str, encounter_rate:int, rarity: CreatureRarity = COMMON, nickname: str = '', caught_date: str = '', sub_environment: str = '', catch_id: int = -1, local_name: str = '', is_favorite: bool = False, is_released: bool = False):
        self.timezone = pytz.timezone('US/Eastern')

        self.creature_id = creature_id
        self.catch_id = catch_id

        self.name = name
        self.local_name = local_name
        self.variant_name = variant_name
        self.nickname = nickname

        self.dex_no = dex_no
        self.variant_no = variant_no

        self.full_name = full_name
        self.scientific_name = scientific_name
        self.kingdom = kingdom
        self.description = description

        self.img_root = img_root + f'_{variant_no}'
        self.sub_environment = sub_environment
        self.encounter_rate = encounter_rate

        self.rarity = rarity
        self.caught_date = caught_date

        self.spawn_time = None
        self.time_to_despawn = None
        self.despawn_time = None
        self.refresh_spawn_and_despawn_time(timezone=self.timezone, minute_offset=0)

        self.is_favorite = is_favorite
        self.is_released = is_released


    def refresh_spawn_and_despawn_time(self, timezone, minute_offset=None):
        self.spawn_time = datetime.datetime.now(pytz.UTC).astimezone(timezone)
        self.time_to_despawn = minute_offset if minute_offset else random.randint(3, 15)
        self.despawn_time = self.spawn_time + datetime.timedelta(minutes=self.time_to_despawn)
        self.time_to_despawn = self.time_to_despawn * 60  # convert to seconds


CURRENT_SPAWN_POOL = [

]

PLACEHOLDER_CREATURE = TGOCreature(creature_id= -1, name='Placeholder Creature', variant_name='', dex_no=0, variant_no=0, full_name='Placeholder Creature', scientific_name='Placeholderus', kingdom='Unknown', description='This is a placeholder creature.', img_root=CHIPMUNK_IMAGE_ROOT, encounter_rate=0, rarity=COMMON)

TEST_CREATURE_COMMON = TGOCreature(creature_id= 1, name='Test Creature - Common', variant_name='', dex_no=1, variant_no=1, full_name='Eastern Chipmunk', scientific_name='Chipmunkus', kingdom='Mammal', description='', img_root=CHIPMUNK_IMAGE_ROOT, encounter_rate=5, rarity=COMMON)
TEST_CREATURE_UNCOMMON = TGOCreature(creature_id= 2, name='Test Creature - Common', variant_name='', dex_no=1, variant_no=1, full_name='Eastern Chipmunk', scientific_name='Chipmunkus', kingdom='Mammal', description='', img_root=CHIPMUNK_IMAGE_ROOT, encounter_rate=5, rarity=UNCOMMON)
TEST_CREATURE_RARE = TGOCreature(creature_id= 3, name='Test Creature - Common', variant_name='', dex_no=1, variant_no=1, full_name='Eastern Chipmunk', scientific_name='Chipmunkus', kingdom='Mammal', description='', img_root=CHIPMUNK_IMAGE_ROOT, encounter_rate=5, rarity=RARE)
TEST_CREATURE_EPIC = TGOCreature(creature_id= 4, name='Test Creature - Common', variant_name='', dex_no=1, variant_no=1, full_name='Eastern Chipmunk', scientific_name='Chipmunkus', kingdom='Mammal', description='', img_root=CHIPMUNK_IMAGE_ROOT, encounter_rate=5, rarity=EPIC)
TEST_CREATURE_LEGENDARY = TGOCreature(creature_id= 5, name='Test Creature - Common', variant_name='', dex_no=1, variant_no=1, full_name='Eastern Chipmunk', scientific_name='Chipmunkus', kingdom='Mammal', description='', img_root=CHIPMUNK_IMAGE_ROOT, encounter_rate=5, rarity=LEGENDARY)

TEST_SPAWN_POOL = [TEST_CREATURE_COMMON, TEST_CREATURE_UNCOMMON, TEST_CREATURE_RARE, TEST_CREATURE_EPIC, TEST_CREATURE_LEGENDARY]

