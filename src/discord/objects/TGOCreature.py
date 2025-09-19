import random

from src.discord.objects.CreatureRarity import COMMON, UNCOMMON, CreatureRarity, RARE, EPIC, LEGENDARY
from src.resources.constants.TGO_MMO_constants import *


class TGOCreature:
    def __init__(self, creature_id: int, name:str, variant_name:str, dex_no: int, variant_no: int, full_name: str, scientific_name: str, kingdom: str, description: str, img_root: str, encounter_rate:int, rarity: CreatureRarity, nickname: str = ''):
        self.creature_id = creature_id

        self.name = name
        self.variant_name = variant_name
        self.nickname = nickname

        self.dex_no = dex_no
        self.variant_no = variant_no

        self.full_name = full_name
        self.scientific_name = scientific_name
        self.kingdom = kingdom
        self.description = description

        self.img_root = img_root + f'_{variant_no}'
        self.encounter_rate = encounter_rate

        self.rarity = rarity
        self.despawn_time = random.randint(1, 15)


CURRENT_SPAWN_POOL = [

]


TEST_CREATURE_COMMON = TGOCreature(creature_id= 1, name='Test Creature - Common', variant_name='', dex_no=1, variant_no=1, full_name='Eastern Chipmunk', scientific_name='Chipmunkus', kingdom='Mammal', description='', img_root=CHIPMUNK_IMAGE_ROOT, encounter_rate=5, rarity=COMMON)
TEST_CREATURE_UNCOMMON = TGOCreature(creature_id= 2, name='Test Creature - Common', variant_name='', dex_no=1, variant_no=1, full_name='Eastern Chipmunk', scientific_name='Chipmunkus', kingdom='Mammal', description='', img_root=CHIPMUNK_IMAGE_ROOT, encounter_rate=5, rarity=UNCOMMON)
TEST_CREATURE_RARE = TGOCreature(creature_id= 3, name='Test Creature - Common', variant_name='', dex_no=1, variant_no=1, full_name='Eastern Chipmunk', scientific_name='Chipmunkus', kingdom='Mammal', description='', img_root=CHIPMUNK_IMAGE_ROOT, encounter_rate=5, rarity=RARE)
TEST_CREATURE_EPIC = TGOCreature(creature_id= 4, name='Test Creature - Common', variant_name='', dex_no=1, variant_no=1, full_name='Eastern Chipmunk', scientific_name='Chipmunkus', kingdom='Mammal', description='', img_root=CHIPMUNK_IMAGE_ROOT, encounter_rate=5, rarity=EPIC)
TEST_CREATURE_LEGENDARY = TGOCreature(creature_id= 5, name='Test Creature - Common', variant_name='', dex_no=1, variant_no=1, full_name='Eastern Chipmunk', scientific_name='Chipmunkus', kingdom='Mammal', description='', img_root=CHIPMUNK_IMAGE_ROOT, encounter_rate=5, rarity=LEGENDARY)

TEST_SPAWN_POOL = [TEST_CREATURE_COMMON, TEST_CREATURE_UNCOMMON, TEST_CREATURE_RARE, TEST_CREATURE_EPIC, TEST_CREATURE_LEGENDARY]

