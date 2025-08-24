import random

from src.discord.objects.CreatureRarity import COMMON, UNCOMMON, CreatureRarity, RARE, EPIC, LEGENDARY
from src.resources.constants.TGO_MMO_constants import *


class TGOCreature:
    def __init__(self, name:str, img_path: str, rarity: str, dex_num: str = '00', variant_name: str = ''):
        self.name = name
        self.variant_name = variant_name
        self.img_path = img_path
        self.thumbnail_path = img_path + "_THUMB"
        self.rarity = rarity
        self.dex_num = dex_num

        self.despawn_time = random.randint(1, 15)


# Define global creature constants
CHIPMUNK_CREATURE = TGOCreature(name='Chipmunk', img_path=CHIPMUNK_IMAGE_FILE, rarity=COMMON, dex_num='01')
DOE_CREATURE = TGOCreature(name='Deer', img_path=DOE_IMAGE_FILE, rarity=COMMON, dex_num='02 A', variant_name='Doe')
BUCK_CREATURE = TGOCreature(name='Deer', img_path=BUCK_IMAGE_FILE, rarity=COMMON, dex_num='02 B', variant_name='Buck')
SQUIRREL_CREATURE = TGOCreature(name='Squirrel', img_path=SQUIRREL_IMAGE_FILE, rarity=COMMON, dex_num='03')
ROBIN_CREATURE = TGOCreature(name='Robin', img_path=ROBIN_IMAGE_FILE, rarity=COMMON, dex_num='04')
SPARROW_M_CREATURE = TGOCreature(name='Sparrow', img_path=SPARROW_M_IMAGE_FILE, rarity=COMMON, dex_num='05 A', variant_name='Male')
SPARROW_F_CREATURE = TGOCreature(name='Sparrow', img_path=SPARROW_M_IMAGE_FILE, rarity=COMMON, dex_num='05 B', variant_name='Female')

BLUEJAY_CREATURE = TGOCreature(name='Bluejay', img_path=BLUEJAY_IMAGE_FILE, rarity=UNCOMMON, dex_num='06')
GOLDFINCH_CREATURE = TGOCreature(name='Gold Finch', img_path=GOLDFINCH_IMAGE_FILE, rarity=UNCOMMON, dex_num='07')
CARDINAL_M_CREATURE = TGOCreature(name='Cardinal', img_path=CARDINAL_M_IMAGE_FILE, rarity=UNCOMMON, dex_num='08 A', variant_name='Male')
CARDINAL_F_CREATURE = TGOCreature(name='Cardinal', img_path=CARDINAL_F_IMAGE_FILE, rarity=UNCOMMON, dex_num='08 B', variant_name='Female')
RACCOON_CREATURE = TGOCreature(name='Raccoon', img_path=RACOON_IMAGE_FILE, rarity=UNCOMMON, dex_num='10')

OWL_CREATURE = TGOCreature(name='Owl', img_path=OWL_IMAGE_FILE, rarity=RARE, dex_num='09')
COYOTE_CREATURE = TGOCreature(name='Coyote', img_path=COYOTE_IMAGE_FILE, rarity=RARE, dex_num='11')

BLACKBEAR_CREATURE = TGOCreature(name='Black Bear', img_path=BLACKBEAR_IMAGE_FILE, rarity=EPIC, dex_num='12')


CURRENT_SPAWN_POOL = [
    CHIPMUNK_CREATURE, DOE_CREATURE, BUCK_CREATURE, SQUIRREL_CREATURE, ROBIN_CREATURE,
    SPARROW_M_CREATURE, SPARROW_F_CREATURE, BLUEJAY_CREATURE, GOLDFINCH_CREATURE, CARDINAL_M_CREATURE,
    CARDINAL_F_CREATURE, OWL_CREATURE, RACCOON_CREATURE, COYOTE_CREATURE, BLACKBEAR_CREATURE
]

TEST_CREATURE_COMMON = TGOCreature(name='Test Creature - Common', img_path=CHIPMUNK_IMAGE_FILE, rarity=COMMON, dex_num='01')
TEST_CREATURE_UNCOMMON = TGOCreature(name='Test Creature - Uncommon', img_path=CHIPMUNK_IMAGE_FILE, rarity=UNCOMMON, dex_num='01')
TEST_CREATURE_RARE = TGOCreature(name='Test Creature - Rare', img_path=CHIPMUNK_IMAGE_FILE, rarity=RARE, dex_num='01')
TEST_CREATURE_EPIC = TGOCreature(name='Test Creature - Epic', img_path=CHIPMUNK_IMAGE_FILE, rarity=EPIC, dex_num='01')
TEST_CREATURE_LEGENDARY = TGOCreature(name='Test Creature - Legendary', img_path=CHIPMUNK_IMAGE_FILE, rarity=LEGENDARY, dex_num='01')

TEST_SPAWN_POOL = [TEST_CREATURE_COMMON, TEST_CREATURE_UNCOMMON, TEST_CREATURE_RARE, TEST_CREATURE_EPIC, TEST_CREATURE_LEGENDARY]

