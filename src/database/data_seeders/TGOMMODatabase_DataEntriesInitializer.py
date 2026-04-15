from src.database.data_seeders.Avatar_DataEntriesInitializer import insert_avatar_data_entries
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.TGO_MMO_creature_constants import *
from src.database.queries.tgommo_avatar_quest_db_queries import *
from src.database.queries.tgommo_create_table_queries import *
from src.database.queries.tgommo_db_queries import *


class TGOMMODatabase_DataEntriesInitializer:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.queryHandler = db_handler.QueryHandler


    def initialize_tgommo_database(self):
        self.create_db_tables()
        self.clear_old_db_table_data()

        self.insert_db_table_data()


    def create_db_tables(self):
        # Basic Object Tables
        self.queryHandler.execute_query(TGOMMO_CREATE_CREATURE_TABLE)
        self.queryHandler.execute_query(TGOMMO_CREATE_ENVIRONMENT_TABLE)

        self.queryHandler.execute_query(TGOMMO_CREATE_USER_PROFILE_TABLE)
        self.queryHandler.execute_query(TGOMMO_CREATE_AVATAR_TABLE)
        self.queryHandler.execute_query(TGOMMO_CREATE_INVENTORY_ITEM_TABLE)

        # Link Tables
        self.queryHandler.execute_query(TGOMMO_CREATE_ENVIRONMENT_CREATURE_TABLE)
        self.queryHandler.execute_query(TGOMMO_CREATE_USER_CREATURE_TABLE)

        self.queryHandler.execute_query(TGOMMO_CREATE_USER_AVATAR_LINK_TABLE)
        self.queryHandler.execute_query(TGOMMO_CREATE_USER_ITEM_INVENTORY_LINK_TABLE)

        self.queryHandler.execute_query(TGOMMO_CREATE_AVATAR_UNLOCK_CONDITION_TABLE)
        self.queryHandler.execute_query(TGOMMO_CREATE_AVATAR_NICKNAME_LINK_TABLE)
        self.queryHandler.execute_query(TGOMMO_CREATE_COLLECTION_TABLE)
    def clear_old_db_table_data(self):
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_CREATURES, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_ENVIRONMENTS, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_ENVIRONMENT_CREATURES, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_AVATAR_UNLOCK_CONDITIONS, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_COLLECTIONS, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_USER_AVATAR, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_INVENTORY_ITEM, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_AVATAR_NICKNAME_LINKS, params=())
        # self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_USER_PROFILE_AVATARS, params=())
    def insert_db_table_data(self):
        # insert creature records
        self.insert_creature_records()
        self.insert_transcendant_creature_records()
        
        self.insert_environment_records()

        insert_avatar_data_entries(self.queryHandler)

        self.insert_collection_records()
        self.insert_item_records()
        self.insert_default_player_records()

        # Link creatures to environments
        self.insert_environment_creature_records()
        self.insert_transcendant_environment_creature_records()

    # ---- INSERT RECORD HELPERS ---- # 
    def insert_creature_records(self):
        creature_data = [
            # region WAVE 1
            ('Deer', 'Doe', 1, 1, 'White-Tailed Deer', 'Odocoileus virginianus', MAMMAL, '', DEER_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Deer', 'Buck', 1, 2, 'White-Tailed Deer', 'Odocoileus virginianus', MAMMAL, '', DEER_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Squirrel', '', 2, 1, 'Eastern Gray Squirrel', 'Sciurus carolinensis', MAMMAL, '', GRAY_SQUIRREL_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Rabbit', '', 3, 1, 'Eastern Cottontail', 'Sylvilagus floridanus', MAMMAL, '', RABBIT_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Chipmunk', '', 4, 1, 'Eastern Chipmunk', 'Tamias striatus', MAMMAL, '', CHIPMUNK_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Raccoon', '', 5, 1, 'Raccoon', 'Procyon lotor', MAMMAL, '', RACOON_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Robin', '', 6, 1, 'American Robin', 'Turdus migratorius', BIRD, '', ROBIN_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Sparrow', 'Male', 7, 1, 'House Sparrow', 'Passer domesticus', BIRD, '', SPARROW_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Sparrow', 'Female', 7, 2, 'House Sparrow', 'Passer domesticus', BIRD, '', SPARROW_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Blue Jay', '', 8, 1, 'Blue Jay', 'Cyanocitta cristata', BIRD, '', BLUEJAY_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Goldfinch', '', 9, 1, 'American Goldfinch', 'Spinus tristis', BIRD, '', GOLDFINCH_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Cardinal', 'Male', 10, 1, 'Northern Cardinal', 'Cardinalis cardinalis', BIRD, '', CARDINAL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Cardinal', 'Female', 10, 2, 'Northern Cardinal', 'Cardinalis cardinalis', BIRD, '', CARDINAL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Monarch', 'Caterpillar', 11, 1, 'Monarch', 'Danaus plexippus', INSECT, '', MONARCH_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Monarch', 'Chrysalis', 11, 2, 'Monarch', 'Danaus plexippus', INSECT, '', MONARCH_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Monarch', 'Butterfly', 11, 3, 'Monarch', 'Danaus plexippus', INSECT, '', MONARCH_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Mantis', '', 12, 1, 'Praying Mantis', 'Stagmomantis carolina', INSECT, '', MANTIS_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Snake', '', 13, 1, 'Eastern Garter Snake', 'Thamnophis sirtalis sirtalis', REPTILE, '', GARTERSNAKE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Turtle', '', 14, 1, 'Box Turtle', 'Terrapene carolina carolina', REPTILE, '', BOX_TURTLE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Toad', '', 15, 1, 'American Toad', 'Anaxyrus americanus', AMPHIBIAN, '', TOAD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Duck', 'Drake', 16, 1, 'Mallard', 'Anas platyrhynchos', BIRD, '', MALLARD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Duck', 'Hen', 16, 2, 'Mallard', 'Anas platyrhynchos', BIRD, '', MALLARD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Turkey', '', 17, 1, 'Wild Turkey', 'Meleagris gallopavo', BIRD, '', TURKEY_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Owl', '', 18, 1, 'Great Horned Owl', 'Bubo virginianus', BIRD, '', GREAT_HORNED_OWL_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Eagle', '', 19, 1, 'Bald Eagle', 'Haliaeetus leucocephalus', BIRD, '', EAGLE_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Opossum', '', 20, 1, 'Virginia Opossum', 'Didelphis virginiana', MAMMAL, '', OPOSSUM_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Fox', '', 21, 1, 'Red Fox', 'Vulpes vulpes', MAMMAL, '', REDFOX_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Bobcat', '', 22, 1, 'Bobcat', 'Lynx rufus', MAMMAL, '', BOBCAT_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Bear', '', 23, 1, 'Black Bear', 'Ursus americanus', MAMMAL, '', BLACKBEAR_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Moose', 'Cow', 24, 1, 'Moose', 'Alces alces', MAMMAL, '', MOOSE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Moose', 'Bull', 24, 2, 'Moose', 'Alces alces', MAMMAL, '', MOOSE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Wolf', '', 25, 1, 'Gray Wolf', 'Canis lupus', MAMMAL, '', WOLF_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            # endregion
            # region WAVE 2
            ('Cat', 'Tabby', 26, 1, 'Domestic Cat', 'Felis catus', MAMMAL, '', CAT_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Cat', 'Black', 26, 2, 'Domestic Cat', 'Felis catus', MAMMAL, '', CAT_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Cat', 'Orange', 26, 3, 'Domestic Cat', 'Felis catus', MAMMAL, '', CAT_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Cat', 'Calico', 26, 4, 'Domestic Cat', 'Felis catus', MAMMAL, '', CAT_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Mouse', '', 27, 1, 'Field Mouse', 'Apodemus', MAMMAL, '', MOUSE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Groundhog', '', 28, 1, 'Groundhog', 'Marmota monax', MAMMAL, '', GROUNDHOG_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Dove', '', 29, 1, 'Mourning Dove', 'Zenaida macroura', BIRD, '', MOURNING_DOVE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Goose', '', 30, 1, 'Canada Goose', 'Branta canadensis', BIRD, '', CANADA_GOOSE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Vulture', '', 31, 1, 'Turkey Vulture', 'Cathartes aura', BIRD, '', TURKEY_VULTURE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Cicada', '', 32, 1, 'Walker’s Cicada', 'Megatibicen pronotalis walkeri', INSECT, '', CICADA_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Cricket', '', 33, 1, 'Field Cricket', 'Gryllus sp.', INSECT, '', CRICKET_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Firefly', '', 34, 1, 'Common Eastern Firefly', 'Photinus pyralis', INSECT, '', FIREFLY_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Luna Moth', '', 35, 1, 'Luna Moth', 'Actias luna', INSECT, '', LUNA_MOTH_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Spider', '', 36, 1, 'Black Widow', 'Latrodectus', ARACHNID, '', BLACK_WIDOW_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Salamander', '', 37, 1, 'Spotted Salamander', 'Ambystoma maculatum', AMPHIBIAN, '', SALAMANDER_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Snapping Turtle', '', 38, 1, 'Common Snapping Turtle', 'Chelydra serpentina', REPTILE, '', SNAPPING_TURTLE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Crow', '', 39, 1, 'American Crow', 'Corvus brachyrhynchos', BIRD, '', AMERICAN_CROW_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Hawk', '', 40, 1, 'Red-Tailed Hawk', 'Buteo jamaicensis', BIRD, '', RED_TAILED_HAWK_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Nighthawk', '', 41, 1, 'Common Nighthawk', 'Chordeiles minor', BIRD, '', NIGHTHAWK_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Woodcock', '', 42, 1, 'American Woodcock', 'Scolopax minor', BIRD, '', WOODCOCK_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Owl', '', 43, 1, 'Eastern Screech Owl', 'Megascops asio', BIRD, '', SCREECH_OWL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Owl', '', 44, 1, 'Snowy Owl', 'Bubo scandiacus', BIRD, '', SNOWY_OWL_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Bat', '', 45, 1, 'Big Brow Bat', 'Eptesicus fuscus', MAMMAL, '', BAT_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Flying Squirrel', '', 46, 1, 'Northern Flying Squirrel', 'Glaucomys sabrinus', MAMMAL, '', FLYING_SQUIRREL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Skunk', '', 47, 1, 'Striped Skunk', 'Mephitis mephitis', MAMMAL, '', SKUNK_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Porcupine', '', 48, 1, 'North American Porcupine', 'Erethizon dorsatum', MAMMAL, '', PORCUPINE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Coyote', '', 49, 1, 'Coyote', 'Canis latrans', MAMMAL, '', COYOTE_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Mountain Lion', '', 50, 1, 'Mountain Lion', 'Puma concolor', MAMMAL, '', MOUNTAIN_LION_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            # endregion
            # region WAVE 3
            ('Skink', '', 51, 1, 'Common Five-lined Skink', 'Plestiodon fasciatus', REPTILE, '', SKINK_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Copperhead', '', 52, 1, 'Eastern Copperhead', 'Plestiodon fasciatus', REPTILE, '', COPPERHEAD_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Worm', '', 53, 1, 'Earth Worm', 'TEMPORARY', CLITELLATA, '', EARTHWORM_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Mole', '', 54, 1, 'Eastern Mole', 'TEMPORARY', MAMMAL, '', EASTERN_MOLE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Mole', '', 55, 1, 'Star-Nosed Mole', 'TEMPORARY', MAMMAL, '', STAR_NOSED_MOLE_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Squirrel', '', 56, 1, 'American Red Squirrel', 'TEMPORARY', MAMMAL, '', RED_SQUIRREL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Ground Squirrel', '', 57, 1, 'Thirteen-Lined Ground Squirrel', 'TEMPORARY', MAMMAL, '', THIRTEEN_LINED_GROUND_SQUIRREL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Stoat', '', 58, 1, 'Stoat', 'TEMPORARY', MAMMAL, '', STOAT_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Boar', '', 59, 1, 'Wild Boar', 'TEMPORARY', MAMMAL, '', BOAR_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Finch', '', 60, 1, 'House Finch', 'TEMPORARY', BIRD, '', HOUSE_FINCH_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Starling', '', 61, 1, 'European Starling', 'TEMPORARY', BIRD, '', STARLING_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Chickadee', '', 62, 1, 'Black-Capped Chickadee', 'TEMPORARY', BIRD, '', BLACK_CAPPED_CHICKADEE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Oriole', '', 63, 1, 'Baltimore Oriole', 'TEMPORARY', BIRD, '', BALTIMORE_ORIOLE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Blackbird', 'Male', 64, 1, 'Red Wing Blackbird', 'TEMPORARY', BIRD, '', REDWING_BLACKBIRD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Blackbird', 'Female', 64, 2, 'Red Wing Blackbird', 'TEMPORARY', BIRD, '', REDWING_BLACKBIRD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Woodpecker', '', 65, 1, 'Pileated Woodpecker', 'TEMPORARY', BIRD, '', PILEATED_WOODPECKER_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Hummingbird', '', 66, 1, 'Ruby-Throated Hummingbird', 'TEMPORARY', BIRD, '', HUMMINGBIRD_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Swallow', '', 67, 1, 'Barn Swallow', 'TEMPORARY', BIRD, '', BARN_SWALLOW_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Owl', '', 68, 1, 'Barn Owl', 'TEMPORARY', BIRD, '', BARN_OWL_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Snail', 'Brown Lipped', 69, 1, 'Brown Lipped Snail', 'Cepaea nemoralis', MOLLUSK, '', SNAIL_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Snail', 'Carthusian', 69, 2, 'Carthusian Snail', 'Monacha cartusiana', MOLLUSK, '', SNAIL_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Snail', 'Garlic', 69, 3, 'Garlic Snail', 'Oxychilus alliarius', MOLLUSK, '', SNAIL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Snail', 'Roman', 69, 4, 'Roman Snail', 'Helix pomatia', MOLLUSK, '', SNAIL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Snail', 'Rosy Wolfsnail', 69, 5, 'Rosy Wolfsnail', 'Euglandina rosea', MOLLUSK, '', SNAIL_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Snail', 'Zebra', 69, 6, 'Zebra Snail', 'Flammulina zebra', MOLLUSK, '', SNAIL_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Snail', 'Amber', 69, 7, 'Amber Snail', 'Succinea', MOLLUSK, '', SNAIL_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Swallowtail', 'Caterpillar', 70, 1, 'Eastern Tiger Swallowtail', 'TEMPORARY', INSECT, '', SWALLOWTAIL_BUTTERFLY_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Swallowtail', 'Butterfly', 70, 2, 'Eastern Tiger Swallowtail', 'TEMPORARY', INSECT, '', SWALLOWTAIL_BUTTERFLY_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Moth', '', 71, 1, 'Tiger Moth', 'TEMPORARY', INSECT, '', TIGER_MOTH_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Moth', '', 72, 1, 'Polyphemus Moth', 'TEMPORARY', INSECT, '', POLYPHEMUS_MOTH_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Honeybee', '', 73, 1, 'Eastern Honeybee', 'TEMPORARY', INSECT, '', HONEYBEE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Ladybug', '', 74, 1, 'Seven-spotted Lady Beetle', 'TEMPORARY', INSECT, '', LADYBUG_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Roly Poly', '', 75, 1, 'Common Pill Woodlouse', 'TEMPORARY', CRUSTACEAN, '', ROLY_POLY_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Lanternfly', '', 76, 1, 'Spotted Lanternfly', 'TEMPORARY', INSECT, '', SPOTTED_LANTERNFLY_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Walkingstick', '', 77, 1, 'Northern Walkingstick', 'TEMPORARY', INSECT, '', NORTHERN_WALKING_STICK_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Dragonfly', '', 78, 1, 'Blue Dasher', 'TEMPORARY', INSECT, '', DRAGONFLY_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Water Strider', '', 79, 1, 'North American Common Water Strider', 'TEMPORARY', INSECT, '', POND_SKATER_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Frog', 'Frog', 80, 1, 'Bull Frog', 'TEMPORARY', AMPHIBIAN, '', BULL_FROG_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Frog', 'Tadpole', 80, 2, 'Bull Frog', 'TEMPORARY', AMPHIBIAN, '', BULL_FROG_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Newt', '', 81, 1, 'Eastern Newt', 'TEMPORARY', AMPHIBIAN, '', EASTERN_NEWT_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Crayfish', '', 82, 1, 'Eastern Crayfish', 'Cambarus bartonii', CRUSTACEAN, '', CRAYFISH_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Turtle', '', 83, 1, 'Painted Turtle', 'Chrysemys picta', REPTILE, '', PAINTED_TURTLE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Killdeer', '', 84, 1, 'Killdeer', 'Charadrius vociferus', BIRD, '', KILLDEER_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Seagull', '', 85, 1, 'Ring-Billed Gull', 'Larus delawarensis', BIRD, '', SEAGULL_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Cormorant', '', 86, 1, 'Double-Crested Cormorant', 'Nannopterum auritum', BIRD, '', CORMORANT_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Kingfisher', '', 87, 1, 'Belted Kingfisher', 'Megaceryle alcyon', BIRD, '', BELTED_KINGFISHER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Loon', '', 88, 1, 'Common Loon', 'Gavia immer', BIRD, '', LOON_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Swan', '', 89, 1, 'Mute Swan', 'Cygnus olor', BIRD, '', MUTE_SWAN_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Heron', '', 90, 1, 'Great Blue Heron', 'Ardea herodias', BIRD, '', GREAT_BLUE_HERON_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Heron', '', 91, 1, 'Black Crowned Night Heron', 'Nycticorax nycticorax', BIRD, '', BLACK_CROWNED_NIGHT_HERON_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Crane', '', 92, 1, 'Sandhill Crane', 'Antigone canadensis', BIRD, '', SANDHILL_CRANE_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Muskrat', '', 93, 1, 'Muskrat', 'Ondatra zibethicus', MAMMAL, '', MUSKRAT_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Beaver', '', 94, 1, 'American Beaver', 'Castor canadensis', MAMMAL, '', BEAVER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Otter', '', 95, 1, 'North American River Otter', 'Lontra canadensis', MAMMAL, '', RIVER_OTTER_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Hercules Beetle', 'Male', 96, 1, 'Eastern Hercules Beetle', 'Dynastes tityus', INSECT, '', HERCULES_BEETLE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Hercules Beetle', 'Female', 96, 2, 'Eastern Hercules Beetle', 'Dynastes tityus', INSECT, '', HERCULES_BEETLE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Hellbender', '', 97, 1, 'Hellbender', 'Cryptobranchus alleganiensis', AMPHIBIAN, '', HELLBENDER_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Puffin', '', 98, 1, 'Atlantic Puffin', 'Fratercula arctica', BIRD, '', PUFFIN_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Seal', '', 99, 1, 'Harbor Seal', 'Phoca vitulina', MAMMAL, '', HARBOR_SEAL_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Alligator', '', 100, 1, 'American Alligator', 'Alligator mississippiensis', REPTILE, '', ALLIGATOR_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            # endregion
            # region WAVE 4
            ('Key Deer', 'Doe', 1, 3, 'Key Deer', 'Odocoileus virginianus clavium', MAMMAL, '', DEER_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Key Deer', 'Buck', 1, 4, 'Key Deer', 'Odocoileus virginianus clavium', MAMMAL, '', DEER_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),

            ('Anole', '', 101, 1, 'Green Anole', 'Anolis carolinensis', REPTILE, '', GREEN_ANOLE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Lizard', '', 102, 1, 'Curly-Tailed Lizard', 'Leiocephalus carinatus', REPTILE, '', CURLY_TAILED_LIZARD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Lizard', '', 103, 1, 'Eastern Glass Lizard', 'Ophisaurus ventralis', REPTILE, '', EASTERN_GLASS_LIZARD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Tortoise', '', 104, 1, 'Gopher Tortoise', 'Gopherus polyphemus', REPTILE, '', GOPHER_TORTOISE_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Turtle', '', 105, 1, 'Florida Softshell Turtle', 'Apalone ferox', REPTILE, '', FLORIDA_SOFTSHELL_TURTLE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Snake', '', 106, 1, 'North American Racer', 'Coluber constrictor', REPTILE, '', NORTH_AMERICAN_RACER_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Snake', '', 107, 1, 'Eastern Coral Snake', 'Micrurus fulvius', REPTILE, '', EASTERN_CORALSNAKE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Tree Frog', '', 108, 1, 'Florida Treefrog', 'Hyla squirella', AMPHIBIAN, '', SQUIRREL_TREEFROG_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Siren', '', 109, 1, 'Greater Siren', 'Siren lacertina', AMPHIBIAN, '', GREATER_SIREN_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Mockingbird', '', 110, 1, 'Northern Mockingbird', 'Mimus polyglottos', BIRD, '', NORTHERN_MOCKINGBIRD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Warbler', '', 111, 1, 'Palm Warbler', 'Setophaga palmarum', BIRD, '', PALM_WARBLER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Warbler', '', 112, 1, 'Yellow-Rumped Warbler', 'Setophaga coronata', BIRD, '', YELLOW_RUMPED_WARBLER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Grackle', '', 113, 1, 'Common Grackle', 'Quiscalus quiscula', BIRD, '', COMMON_GRACKLE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Bunting', 'Male', 114, 1, 'Painted Bunting', 'Passerina ciris', BIRD, '', PAINTED_BUNTING_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Bunting', 'Female', 114, 2, 'Painted Bunting', 'Passerina ciris', BIRD, '', PAINTED_BUNTING_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Pigeon', '', 115, 1, 'White-Crowned Pigeon', 'Patagioenas leucocephala', BIRD, '', WHITE_CROWNED_PIGEON_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Vulture', '', 116, 1, 'Black Vulture', 'Coragyps atratus', BIRD, '', BLACK_VULTURE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Hawk', '', 117, 1, 'Red-Shouldered Hawk', 'Buteo lineatus', BIRD, '', RED_SHOULDERED_HAWK_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Osprey', '', 118, 1, 'Osprey', 'Pandion haliaetus', BIRD, '', OSPREY_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Owl', '', 119, 1, 'Barred Owl', 'Strix varia', BIRD, '', BARRED_OWL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Caracara', '', 120, 1, 'Crested Caracara', 'Caracara cheriway', BIRD, '', CRESTED_CARACARA_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Kite', '', 121, 1, 'Swallow-Tailed Kite', 'Elanoides forficatus', BIRD, '', SWALLOW_TAILED_KITE_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Duck', '', 122, 1, 'Black Bellied Whistling Duck', 'Dendrocygna autumnalis', BIRD, '', BLACK_BELLIED_WHISTLING_DUCK_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Gallinule', '', 123, 1, 'Purple Gallinule', 'Porphyrio martinicus', BIRD, '', PURPLE_GALLINULE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Heron', '', 124, 1, 'Little Blue Heron', 'Egretta caerulea', BIRD, '', LITTLE_BLUE_HERON_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Heron', '', 125, 1, 'Yellow-Crowned Night Heron', 'Nyctanassa violacea', BIRD, '', YELLOW_CROWNED_NIGHT_HERON_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Egret', '', 126, 1, 'Great Egret', 'Ardea alba', BIRD, '', GREAT_EGRET_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Egret', '', 127, 1, 'Reddish Egret', 'Egretta rufescens', BIRD, '', REDDISH_EGRET_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Ibis', '', 128, 1, 'White Ibis', 'Eudocimus albus', BIRD, '', WHITE_IBIS_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Anhinga', '', 129, 1, 'Anhinga', 'Anhinga anhinga', BIRD, '', ANHINGA_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Stork', '', 130, 1, 'Wood Stork', 'Mycteria americana', BIRD, '', WOOD_STORK_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Spoonbill', '', 131, 1, 'Roseate Spoonbill', 'Platalea ajaja', BIRD, '', SPOONBILL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Mosquito', '', 132, 1, 'Common Mosquito', 'Culex pipiens', INSECT, '', MOSQUITO_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Fritillary', 'Caterpillar', 133, 1, 'Gulf Fritillary', 'Agraulis vanillae', INSECT, '', GULF_FRITILLARY_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Fritillary', 'Butterfly', 133, 2, 'Gulf Fritillary', 'Agraulis vanillae', INSECT, '', GULF_FRITILLARY_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Butterfly', '', 134, 1, 'Zebra Longwing', 'Heliconius charithonia', INSECT, '', ZEBRA_LONGWING_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Butterfly', '', 135, 1, 'Atala Butterfly', 'Eumaeus atala', INSECT, '', ATALA_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Dragonfly', '', 136, 1, 'Eastern Pondhawk', 'Erythemis simplicicollis', INSECT, '', EASTERN_PONDHAWK_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Grasshopper', '', 137, 1, 'Eastern Lubber Grasshopper', 'Romalea microptera', INSECT, '', LUBBER_GRASSHOPPER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Spider', '', 138, 1, 'Golden Silk Orb-Weaver', 'Nephila clavipes', ARACHNID, '', GOLDEN_ORB_WEAVER_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Spider', '', 139, 1, 'Spiny Orb-Weaver', 'Gasteracantha cancriformis', ARACHNID, '', SPINY_ORB_WEAVER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Millipede', '', 140, 1, 'Bumblebee Millipede', 'TEMPORARY', MYRIAPOD, '', BUMBLEBEE_MILLIPEDE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Snail', '', 141, 1, 'Florida Tree Snail', 'Conus floridanus', MOLLUSK, '', FLORIDA_TREE_SNAIL_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Armadillo', '', 142, 1, 'Nine-Banded Armadillo', 'Dasypus novemcinctus', MAMMAL, '', NINE_BANDED_ARMADILLO_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Squirrel', '', 143, 1, 'Fox Squirrel', 'Sciurus niger', MAMMAL, '', FOX_SQUIRREL_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Mink', '', 144, 1, 'American Mink', 'Neogale vison', MAMMAL, '', MINK_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Fox', '', 145, 1, 'Gray Fox', 'Urocyon cinereoargenteus', MAMMAL, '', GRAY_FOX_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Tern', '', 146, 1, 'Royal Tern', 'Thalasseus maximus', BIRD, '', ROYAL_TERN_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Gull', '', 147, 1, 'Laughing Gull', 'Leucophaeus atricilla', BIRD, '', LAUGHING_GULL_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Pelican', '', 148, 1, 'Brown Pelican', 'Pelecanus occidentalis', BIRD, '', BROWN_PELICAN_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Pelican', '', 149, 1, 'American White Pelican', 'Pelecanus erythrorhynchos', BIRD, '', AMERICAN_WHITE_PELICAN_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Frigatebird', 'Male', 150, 1, 'Magnificent Frigatebird', 'Fregata magnificens', BIRD, '', MAGNIFICENT_FRIGATEBIRD_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Frigatebird', 'Female', 150, 2, 'Magnificent Frigatebird', 'Fregata magnificens', BIRD, '', MAGNIFICENT_FRIGATEBIRD_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Crab', '', 151, 1, 'Atlantic Ghost Crab', 'Ocypode quadrata', CRUSTACEAN, '', ATLANTIC_GHOST_CRAB_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Crab', '', 152, 1, 'Atlantic Blue Crab', 'Callinectes sapidus', CRUSTACEAN, '', ATLANTIC_BLUE_CRAB_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Horseshoe Crab', '', 153, 1, 'Horseshoe Crab', 'Limulus polyphemus', ARTHROPOD, '', HORSESHOE_CRAB_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Conch', '', 154, 1, 'Conch', 'Lobatus gigas', MOLLUSK, '', CONCH_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Hermit Crab', '', 155, 1, 'Caribean Land Hermit Crab', 'Coenobita clypeatus', CRUSTACEAN, '', CARIBBEAN_LAND_HERMIT_CRAB_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Sea Turtle', '', 156, 1, 'Green Sea Turtle', 'Chelonia mydas', REPTILE, '', GREEN_SEA_TURTLE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Manatee', '', 157, 1, 'West Indian Manatee', 'Trichechus manatus', MAMMAL, '', WEST_INDIAN_MANATEE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Dolphin', '', 158, 1, 'Bottlenose Dolphin', 'Tursiops truncatus', MAMMAL, '', BOTTLENOSE_DOLPHIN_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Flamingo', '', 159, 1, 'American Flamingo', 'Phoenicopterus ruber', BIRD, '', AMERICAN_FLAMINGO_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Crocodile', '', 160, 1, 'American Crocodile', 'Crocodylus acutus', REPTILE, '', AMERICAN_CROCODILE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Anole', '', 161, 1, 'Brown Anole', 'Anolis sagrei', REPTILE, '', BROWN_ANOLE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Agama', 'Male', 162, 1, "Peters' Rock Agama", 'Agama picticauda', REPTILE, '', PETERS_ROCK_AGAMA_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Agama', 'Female', 162, 2, "Peters' Rock Agama", 'Agama picticauda', REPTILE, '', PETERS_ROCK_AGAMA_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Iguana', '', 163, 1, 'Green Iguana', 'Iguana iguana', REPTILE, '', GREEN_IGUANA_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Python', '', 164, 1, 'Burmese Python', 'Python bivittatus', REPTILE, '', RETICULATED_PYTHON_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Gecko', '', 165, 1, 'Tokay Gecko', 'Gekko gecko', REPTILE, '', TOKAY_GECKO_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Chameleon', '', 166, 1, "Jackson's Chameleon", 'Trioceros jacksonii', REPTILE, '', JACKSONS_CHAMELEON_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Toad', '', 167, 1, 'Cane Toad', 'Rhinella marina', AMPHIBIAN, '', CANE_TOAD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Myna', '', 168, 1, 'Common Myna', 'Acridotheres tristis', BIRD, '', COMMON_MYNA_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Chicken', 'Hen', 169, 1, 'Red Junglefowl', 'Gallus gallus', BIRD, '', DOMESTIC_CHICKEN_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Chicken', 'Rooster', 169, 2, 'Red Junglefowl', 'Gallus gallus', BIRD, '', DOMESTIC_CHICKEN_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Chicken', 'Chick', 169, 3, 'Red Junglefowl', 'Gallus gallus', BIRD, '', DOMESTIC_CHICKEN_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Duck', '', 170, 1, 'Muscovy Duck', 'Cairina moschata', BIRD, '', MUSCOVY_DUCK_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Goose', '', 171, 1, 'Egyptian Goose', 'Alopochen aegyptiaca', BIRD, '', EGYPTIAN_GOOSE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Peafowl', 'Peacock', 172, 1, 'Indian Peafowl', 'Pavo cristatus', BIRD, '', INDIAN_PEAFOWL_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Peafowl', 'Peahen', 172, 2, 'Indian Peafowl', 'Pavo cristatus', BIRD, '', INDIAN_PEAFOWL_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Monkey', '', 173, 1, 'Green Monkey', 'Chlorocebus sabaeus', MAMMAL, '', GREEN_MONKEY_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Monkey', '', 174, 1, 'Rhesus Macaque', 'Macaca mulatta', MAMMAL, '', RHESUS_MACAQUE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Capybara', '', 175, 1, 'Capybara', 'Hydrochoerus hydrochaeris', MAMMAL, '', CAPYBARA_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Dog', 'Mutt', 176, 1, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Dog', 'German Shepherd', 176, 2, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Dog', 'Beagle', 176, 3, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Dog', 'Labrador', 176, 4, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Dog', 'Chihuahua', 176, 5, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Dog', 'Great Dane', 176, 6, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Dog', 'Dalmatian', 176, 7, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Dog', 'Corgi', 176, 8, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Dog', 'Dachshund', 176, 9, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Dog', 'Pug', 176, 10, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            # endregion
            # region WAVE 4.5
            ('Dog', 'Poodle', 176, 11, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),

            ('Pigeon', '', 177, 1, 'Rock Pigeon', 'Columba livia', BIRD, '', ROCK_PIGEON_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Rat', '', 178, 1, 'Brown Rat', 'Rattus norvegicus', MAMMAL, '', BROWN_RAT_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Horse', '', 179, 1, 'Domestic Horse', 'Equus ferus caballus', MAMMAL, '', DOMESTIC_HORSE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Ant', 'Worker', 180, 1, 'Carpenter Ant', 'Camponotus pennsylvanicus', INSECT, '', CARPENTER_ANT_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Ant', 'Queen', 180, 2 , 'Carpenter Ant', 'Camponotus pennsylvanicus', INSECT, '', CARPENTER_ANT_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Yellowjacket', '', 181, 1, 'Eastern Yellowjacket', 'Vespula maculifrons', INSECT, '', YELLOW_JACKET_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Leafhopper', '', 182, 1, 'Red Banded Leafhopper', 'Graphocephala coccinea', INSECT, '', RED_BANDED_LEAFHOPPER_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Butterfly', '', 183, 1, 'Cabbage White Butterfly', 'Pieris rapae', INSECT, '', CABBAGE_WHITE_BUTTERFLY_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Butterfly', '', 184, 1, 'Orange Sulphur Butterfly', 'Colias eurytheme', INSECT, '', ORANGE_SULPHUR_BUTTERFLY_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Toe Biter', '', 185, 1, 'Giant Water Bug', 'Lethocerus americanus', INSECT, '', GIANT_WATERBUG_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Beetle', '', 186, 1, 'Japanese Beetle', 'Popillia japonica', INSECT, '', JAPANESE_BEETLE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Salamander', '', 187, 1, 'Red-Backed Salamander', 'Plethodon cinereus', AMPHIBIAN, '', RED_BACKED_SALAMANDER_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Peeper', '', 188, 1, 'Spring Peeper', 'Pseudacris crucifer', AMPHIBIAN, '', SPRING_PEEPER_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Tree Frog', '', 189, 1, 'Cuban Tree Frog', 'Osteopilus septentrionalis', AMPHIBIAN, '', CUBAN_TREE_FROG_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Monitor', '', 190, 1, 'Nile Monitor', 'Varanus niloticus', REPTILE, '', NILE_MONITOR_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Tegu', '', 191, 1, 'Argentine Black and White Tegu', 'Salvator merianae', REPTILE, '', ARGENTINE_BLACK_AND_WHITE_TEGU_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Bluebird', '', 192, 1, 'Eastern Bluebird', 'Sialia sialis', BIRD, '', EASTERN_BLUEBIRD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Heron', '', 193, 1, 'Green Heron', 'Butorides virescens', BIRD, '', GREEN_HERON_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Bobwhite', '', 194, 1, 'Northern Bobwhite', 'Colinus virginianus', BIRD, '', NORTHERN_BOBWHITE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Pheasant', 'Male', 195, 1, 'Ring-Necked Pheasant', 'Phasianus colchicus', BIRD, '', RING_NECKED_PHEASANT_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Pheasant', 'Female', 195, 2, 'Ring-Necked Pheasant', 'Phasianus colchicus', BIRD, '', RING_NECKED_PHEASANT_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Parakeet', 'Green', 196, 1, 'Monk Parakeet', 'Myiopsitta monachus', BIRD, '', MONK_PARAKEET_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Parakeet', 'Blue', 196, 2, 'Monk Parakeet', 'Myiopsitta monachus', BIRD, '', MONK_PARAKEET_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Parakeet', 'Yellow', 196, 3, 'Monk Parakeet', 'Myiopsitta monachus', BIRD, '', MONK_PARAKEET_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Parakeet', 'White', 196, 4, 'Monk Parakeet', 'Myiopsitta monachus', BIRD, '', MONK_PARAKEET_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Macaw', '', 197, 1, 'Scarlet Macaw', 'Ara macao', BIRD, '', SCARLET_MACAW_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Shrew', '', 198, 1, 'Northern Short-Tailed Shrew', 'Blarina brevicauda', MAMMAL, '', NORTHERN_SHORT_TAILED_SHREW_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Elk', 'Female', 199, 1, 'Elk', 'Cervus canadensis', MAMMAL, '', ELK_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Elk', 'Male', 199, 2, 'Elk', 'Cervus canadensis', MAMMAL, '', ELK_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Wolf', '', 200, 1, 'Red Wolf', 'Canis rufus', MAMMAL, '', RED_WOLF_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            # endregion
            # region WAVE 5
            ('Dog', 'Husky', 176, 12, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Dog', 'Collie', 176, 13, 'Domestic Dog', 'Canis lupus familiaris', MAMMAL, '', DOMESTIC_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Horse', '', 179, 1, 'Domestic Horse', 'Equus ferus caballus', MAMMAL, '', DOMESTIC_HORSE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),

            ('Hare', '', 201, 1, 'Arctic Hare', 'Lepus arcticus', MAMMAL, '', ARCTIC_HARE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Hare', '', 202, 1, 'Snowshoe Hare', 'Lepus americanus', MAMMAL, '', SNOWSHOE_HARE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Lemming', '', 203, 1, 'Northern Collared Lemming', 'Dicrostonyx groenlandicus', MAMMAL, '', NORTHERN_COLLARED_LEMMING_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Pika', '', 204, 1, 'American Pika', 'Ochotona princeps', MAMMAL, '', PIKA_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Marmot', '', 205, 1, 'Hoary Marmot', 'Marmota caligata', MAMMAL, '', HOARY_MARMOT_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Prairie Dog', '', 206, 1, 'Black-tailed Prairie Dog', 'Cynomys ludovicianus', MAMMAL, '', BLACK_TAILED_PRAIRIE_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Prairie Dog', '', 207, 1, 'White-tailed Prairie Dog', 'Cynomys leucurus', MAMMAL, '', WHITE_TAILED_PRAIRIE_DOG_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Badger', '', 208, 1, 'American Badger', 'Taxidea taxus', MAMMAL, '', AMERICAN_BADGER_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Marten', '', 209, 1, 'American Pine Marten', 'Martes americana', MAMMAL, '', PINE_MARTEN_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Ferret', '', 210, 1, 'Black-footed Ferret', 'Mustela nigripes', MAMMAL, '', BLACK_FOOTED_FERRET_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Sheep', '', 211, 1, 'Domestic Sheep', 'Ovis aries', MAMMAL, '', DOMESTIC_SHEEP_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Sheep', '', 212, 1, 'Bighorn Sheep', 'Ovis canadensis', MAMMAL, '', BIGHORN_SHEEP_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Mountain Goat', '', 213, 1, 'Mountain Goat', 'Oreamnos americanus', MAMMAL, '', MOUNTAIN_GOAT_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Caribou', '', 214, 1, 'Caribou', 'Rangifer tarandus', MAMMAL, '', CARIBOU_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Musk Ox', '', 215, 1, 'Musk Ox', 'Ovibos moschatus', MAMMAL, '', MUSK_OX_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Bison', '', 216, 1, 'American Bison', 'Bison bison', MAMMAL, '', AMERICAN_BISON_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Pronghorn', '', 217, 1, 'Pronghorn', 'Antilocapra americana', MAMMAL, '', PRONGHORN_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Fly', '', 218, 1, 'House Fly', 'Musca domestica', INSECT, '', FLY_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Fly', '', 219, 1, 'Yellow Dung Fly', 'Scathophaga stercoraria', INSECT, '', GOLDEN_DUNG_FLY_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Bumblebee', '', 220, 1, 'Bumblebee', 'Bombus species', INSECT, '', BUMBLEBEE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Slug', '', 221, 1, 'Black Slug', 'Limax maximus', MOLLUSK, '', BLACK_SLUG_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Spider', '', 222, 1, 'Wolf Spider', 'Lycosa species', ARACHNID, '', WOLF_SPIDER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Spider', '', 223, 1, 'Cross Orbweaver', 'Araneus diadematus', ARACHNID, '', CROSS_ORBWEAVER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Harvestman', '', 224, 1, 'Harvestman', 'Opilio parietinus', ARACHNID, '', HARVESTMAN_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Sphinx Moth', 'Caterpillar', 225, 1, 'White-lined Sphinx Moth', 'Hyles lineata', INSECT, '', WHITE_LINED_SPHINX_MOTH_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Sphinx Moth', 'Moth', 225, 2, 'White-lined Sphinx Moth', 'Hyles lineata', INSECT, '', WHITE_LINED_SPHINX_MOTH_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Beetle', '', 226, 1, 'Ornate Checkered Beetle', 'Trichodes ornatus', INSECT, '', ORNATE_CHECKERED_BEETLE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Moth', '', 227, 1, 'Western Sheep Moth', 'Hemileuca eglanterina', INSECT, '', WESTERN_SHEEP_MOTH_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Snake', '', 228, 1, 'Smooth Greensnake', 'Opheodrys vernalis', REPTILE, '', SMOOTH_GREENSNAKE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Rattlesnake', '', 229, 1, 'Prairie Rattlesnake', 'Crotalus viridis', REPTILE, '', PRAIRIE_RATTLESNAKE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Lizard', '', 230, 1, 'Greater Short-horned Lizard', 'Phrynosoma hernandesi', REPTILE, '', SHORT_HORNED_LIZARD_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Lizard', '', 231, 1, 'Desert Collared Lizard', 'Crotaphytus bicinctores', REPTILE, '', DESERT_COLLARED_LIZARD_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Frog', '', 232, 1, 'Northern Leopard Frog', 'Lithobates pipiens', AMPHIBIAN, '', LEOPARD_FROG_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Toad', '', 233, 1, 'Western Toad', 'Anaxyrus boreas', AMPHIBIAN, '', WESTERN_TOAD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Salamander', '', 234, 1, 'Barred Tiger Salamander', 'Ambystoma mavortium', AMPHIBIAN, '', TIGER_SALAMANDER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Redwing', '', 235, 1, 'Redwing', 'Turdus iliacus', BIRD, '', REDWING_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Blackbird', '', 236, 1, 'Eurasian Blackbird', 'Turdus merula', BIRD, '', EURASIAN_BLACKBIRD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Wagtail', '', 237, 1, 'White Wagtail', 'Motacilla alba', BIRD, '', WHITE_WAGTAIL_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Redpoll', '', 238, 1, 'Common Redpoll', 'Acanthis flammea', BIRD, '', COMMON_REDPOLL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Bunting', '', 239, 1, 'Snow Bunting', 'Plectrophenax nivalis', BIRD, '', SNOW_BUNTING_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Longspur', '', 240, 1, 'Lapland Longspur', 'Calcarius lapponicus', BIRD, '', LAPLAND_LONGSPUR_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Raven', '', 241, 1, 'Common Raven', 'Corvus corax', BIRD, '', COMMON_RAVEN_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Magpie', '', 242, 1, 'Black-billed Magpie', 'Pica hudsonia', BIRD, '', BLACK_BILLED_MAGPIE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Stellar\'s Jay', '', 243, 1, 'Steller\'s Jay', 'Cyanocitta stelleri', BIRD, '', STELLARS_JAY_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Bluebird', '', 244, 1, 'Mountain Bluebird', 'Sialia currucoides', BIRD, '', MOUNTAIN_BLUEBIRD_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Chickadee', '', 245, 1, 'Mountain Chickadee', 'Poecile gambeli', BIRD, '', MOUNTAIN_CHICKADEE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Waxwing', '', 246, 1, 'Cedar Waxwing', 'Bombycilla cedrorum', BIRD, '', CEDAR_WAXWING_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Blackbird', '', 247, 1, 'Yellow-headed Blackbird', 'Xanthocephalus xanthocephalus', BIRD, '', YELLOW_HEADED_BLACKBIRD_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Goldfinch', '', 248, 1, 'Lesser Goldfinch', 'Spinus psaltria', BIRD, '', LESSER_GOLDFINCH_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Finch', '', 249, 1, 'Gray-crowned Rosy-Finch', 'Leucosticte tephrocotis', BIRD, '', GRAY_CROWNED_ROSY_FINCH_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Nutcracker', '', 250, 1, 'Clark\'s Nutcracker', 'Nucifraga columbiana', BIRD, '', CLARKS_NUTCRACKER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Flicker', '', 251, 1, 'Northern Flicker', 'Colaptes auratus', BIRD, '', NORTHERN_FLICKER_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Woodpecker', '', 252, 1, 'Lewis\'s Woodpecker', 'Melanerpes lewis', BIRD, '', LEWIS_WOODPECKER_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Tanager', '', 253, 1, 'Western Tanager', 'Piranga ludoviciana', BIRD, '', WESTERN_TANAGER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Swallow', '', 254, 1, 'Tree Swallow', 'Tachycineta bicolor', BIRD, '', TREE_SWALLOW_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Swallow', '', 255, 1, 'Violet-green Swallow', 'Tachycineta thalassina', BIRD, '', VIOLET_GREEN_SWALLOW_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Ptarmigan', '', 256, 1, 'Rock Ptarmigan', 'Lagopus muta', BIRD, '', ROCK_PTARMIGAN_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Grouse', '', 257, 1, 'Greater Sage-Grouse', 'Centrocercus urophasianus', BIRD, '', GREATER_SAGE_GROUSE_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Grouse', '', 258, 1, 'Dusky Grouse', 'Dendragapus obscurus', BIRD, '', DUSKY_GROUSE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Prairie Chicken', '', 259, 1, 'Greater Prairie-Chicken', 'Tympanuchus cupido', BIRD, '', AMERICAN_PRAIRIE_CHICKEN_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Dipper', '', 260, 1, 'American Dipper', 'Cinclus mexicanus', BIRD, '', AMERICAN_DIPPER_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Avocet', '', 261, 1, 'American Avocet', 'Recurvirostra americana', BIRD, '', AMERICAN_AVOCET_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Ibis', '', 262, 1, 'White-faced Ibis', 'Plegadis chihi', BIRD, '', WHITE_FACED_IBIS_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Stilt', '', 263, 1, 'Black-necked Stilt', 'Himantopus mexicanus', BIRD, '', BLACK_NECKED_STILT_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Eider', 'Male', 264, 1, 'Common Eider', 'Somateria mollissima', BIRD, '', COMMON_EIDER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Eider', 'Female', 264, 2, 'Common Eider', 'Somateria mollissima', BIRD, '', COMMON_EIDER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Eider', '', 265, 1, 'King Eider', 'Somateria spectabilis', BIRD, '', KING_EIDER_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Duck', 'Male', 266, 1, 'Tufted Duck', 'Aythya fuligula', BIRD, '', TUFTED_DUCK_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Duck', 'Female', 266, 2, 'Tufted Duck', 'Aythya fuligula', BIRD, '', TUFTED_DUCK_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Duck', '', 267, 1, 'Harlequin Duck', 'Histrionicus histrionicus', BIRD, '', HARLEQUIN_DUCK_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Duck', '', 268, 1, 'Long-tailed Duck', 'Clangula hyemalis', BIRD, '', LONG_TAILED_DUCK_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Merganser', 'Male', 269, 1, 'Common Merganser', 'Mergus merganser', BIRD, '', COMMON_MERGANSER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Merganser', 'Female', 269, 2, 'Common Merganser', 'Mergus merganser', BIRD, '', COMMON_MERGANSER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Merganser', '', 270, 1, 'Hooded Merganser', 'Lophodytes cucullatus', BIRD, '', HOODED_MERGANSER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Goose', '', 271, 1, 'Greylag Goose', 'Anser anser', BIRD, '', GREYLAG_GOOSE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Goose', '', 272, 1, 'Barnacle Goose', 'Branta leucopsis', BIRD, '', BARNACLE_GOOSE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Goose', '', 273, 1, 'Snow Goose', 'Anser caerulescens', BIRD, '', SNOW_GOOSE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Swan', '', 274, 1, 'Whooper Swan', 'Cygnus cygnus', BIRD, '', WHOOPER_SWAN_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Grebe', '', 275, 1, 'Horned Grebe', 'Podiceps auritus', BIRD, '', HORNED_GREBE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Grebe', '', 276, 1, 'Western Grebe', 'Aechmophorus occidentalis', BIRD, '', WESTERN_GREBE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Falcon', '', 277, 1, 'Peregrine Falcon', 'Falco peregrinus', BIRD, '', PEREGRINE_FALCON_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Gyrfalcon', '', 278, 1, 'Gyrfalcon', 'Falco rusticolus', BIRD, '', GYRFALCON_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Eagle', '', 279, 1, 'White-tailed Eagle', 'Haliaeetus albicilla', BIRD, '', WHITE_TAILED_EAGLE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Eagle', '', 280, 1, 'Golden Eagle', 'Aquila chrysaetos', BIRD, '', GOLDEN_EAGLE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Owl', '', 281, 1, 'Great Gray Owl', 'Strix nebulosa', BIRD, '', GREAT_GRAY_OWL_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Crab', '', 282, 1, 'European Green Crab', 'Carcinus maenas', CRUSTACEAN, '', EUROPEAN_GREEN_CRAB_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Barnacle', '', 283, 1, 'Acorn Barnacle', 'Semibalanus balanoides', CRUSTACEAN, '', ACORN_BARNACLE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Whelk', '', 284, 1, 'Common Whelk', 'Buccinum undatum', MOLLUSK, '', WHELK_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Mussel', '', 285, 1, 'Blue Mussel', 'Mytilus edulis', MOLLUSK, '', MUSSEL_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Sea Star', '', 286, 1, 'Common Sea Star', 'Asterias rubens', ASTEROIDEA, '', COMMON_SEA_STAR_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Redshank', '', 287, 1, 'Common Redshank', 'Tringa totanus', BIRD, '', COMMON_REDSHANK_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Sandpiper', '', 288, 1, 'Purple Sandpiper', 'Calidris maritima', BIRD, '', PURPLE_SANDPIPER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Plover', '', 289, 1, 'European Golden-Plover', 'Pluvialis apricaria', BIRD, '', GOLDEN_PLOVER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Phalarope', '', 290, 1, 'Red-necked Phalarope', 'Phalaropus lobatus', BIRD, '', RED_NECKED_PHALAROPE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Oystercatcher', '', 291, 1, 'Eurasian Oystercatcher', 'Haematopus ostralegus', BIRD, '', EURASIAN_OYSTERCATCHER_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Ruff', '', 292, 1, 'Ruff', 'Calidris pugnax', BIRD, '', RUFF_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Shag', '', 293, 1, 'European Shag', 'Phalacrocorax aristotelis', BIRD, '', EUROPEAN_SHAG_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Gull', '', 294, 1, 'Glaucous Gull', 'Larus hyperboreus', BIRD, '', GLAUCOUS_GULL_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Kittiwake', '', 295, 1, 'Black-legged Kittiwake', 'Rissa tridactyla', BIRD, '', BLACK_LEGGED_KITTIWAKE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Fulmar', '', 296, 1, 'Northern Fulmar', 'Fulmarus glacialis', BIRD, '', NORTHERN_FULMAR_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Gannet', '', 297, 1, 'Northern Gannet', 'Morus bassanus', BIRD, '', NORTHERN_GANNET_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Jaeger', '', 298, 1, 'Long-tailed Jaeger', 'Stercorarius longicaudus', BIRD, '', LONG_TAILED_JAEGER_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Dovekie', '', 299, 1, 'Dovekie', 'Alle alle', BIRD, '', DOVEKIE_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Guillemot', '', 300, 1, 'Black Guillemot', 'Cepphus grylle', BIRD, '', BLACK_GUILLEMOT_IMAGE_ROOT, 5, TGOMMO_RARITY_UNCOMMON),
            ('Razorbill', '', 301, 1, 'Razorbill', 'Alca torda', BIRD, '', RAZORBILL_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Seal', '', 302, 1, 'Gray Seal', 'Halichoerus grypus', MAMMAL, '', GRAY_SEAL_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Walrus', '', 303, 1, 'Walrus', 'Odobenus rosmarus', MAMMAL, '', WALRUS_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Porpoise', '', 304, 1, 'Harbor Porpoise', 'Phocoena phocoena', MAMMAL, '', HARBOR_PORPOISE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Beluga', '', 305, 1, 'Beluga Whale', 'Delphinapterus leucas', MAMMAL, '', BELUGA_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Whale', '', 306, 1, 'Humpback Whale', 'Megaptera novaeangliae', MAMMAL, '', HUMPBACK_WHALE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Fox', '', 307, 1, 'Arctic Fox', 'Vulpes lagopus', MAMMAL, '', ARCTIC_FOX_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('Lynx', '', 308, 1, 'Canada Lynx', 'Lynx canadensis', MAMMAL, '', CANADA_LYNX_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Wolverine', '', 309, 1, 'Wolverine', 'Gulo gulo', MAMMAL, '', WOLVERINE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Bear', '', 310, 1, 'Grizzly Bear', 'Ursus arctos horribilis', MAMMAL, '', GRIZZLY_BEAR_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Bear', '', 311, 1, 'Polar Bear', 'Ursus maritimus', MAMMAL, '', POLAR_BEAR_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            # endregion
        ]

        for index, creature in enumerate(creature_data):
            creature = (index + 1,) + creature
            self.queryHandler.execute_query(TGOMMO_INSERT_NEW_CREATURE, params=creature)
    def insert_transcendant_creature_records(self):
        transcendant_creature_data = [
            ('Bigfoot', '', BIGFOOT_DEX_NO, 1, 'Sasquatch', 'N/A', MYSTICAL, '', BIGFOOT_IMAGE_ROOT, 5, TGOMMO_RARITY_TRANSCENDANT),
            ('Mothman', '', MOTHMAN_DEX_NO, 1, 'Mothman', 'N/A', MYSTICAL, '', MOTHMAN_IMAGE_ROOT, 5, TGOMMO_RARITY_TRANSCENDANT),
            ('Frogman', '', FROGMAN_DEX_NO, 1, 'Loveland Frogman', 'N/A', MYSTICAL, '', FROGMAN_IMAGE_ROOT, 5, TGOMMO_RARITY_TRANSCENDANT),
            ('Skunk Ape', '', SKUNK_APE_DEX_NO, 1, 'Skunk Ape', 'N/A', MYSTICAL, '', SKUNK_APE_IMAGE_ROOT, 5, TGOMMO_RARITY_TRANSCENDANT),
            ('Chupacabra', '', CHUPACABRA_DEX_NO, 1, 'Chupacabra', 'N/A', MYSTICAL, '', CHUPACABRA_IMAGE_ROOT, 5, TGOMMO_RARITY_TRANSCENDANT),
            ('Wampus Cat', '', WAMPUS_CAT_DEX_NO, 1, 'Wampus Cat', 'N/A', MYSTICAL, '', WAMPUS_CAT_IMAGE_ROOT, 5, TGOMMO_RARITY_TRANSCENDANT),
            # ('Jersey Devil', '', JERSEY_DEVIL_DEX_NO, 1, 'Jersey Devil', 'N/A', MAMMAL, '', JERSEY_DEVIL_IMAGE_ROOT, 5),
            # ('Thunderbird', '', THUNDERBIRD_DEX_NO, 1, 'Thunderbird', 'N/A', BIRD, '', THUNDERBIRD_IMAGE_ROOT, 5),
        ]

        for index, creature in enumerate(transcendant_creature_data):
            creature = (9000 + index + 1,) + creature
            self.queryHandler.execute_query(TGOMMO_INSERT_NEW_CREATURE, params=creature)

    def insert_environment_records(self):
        # Base environment data without day/night variants
        base_environment_data = [
            ('Eastern United States', '', EASTERN_US_DEX_NO, 'Eastern United States', '', 'est_us', EASTERN_US_IMAGE_ROOT_SUFFIX),
            ('Everglades National Park', '', FLORIDA_DEX_NO, 'Florida', '', 'florida', EVERGLADES_IMAGE_ROOT_SUFFIX),
            ('Iceland', '', ICELAND_DEX_NO, 'Iceland', '', 'iceland', ICELAND_IMAGE_ROOT_SUFFIX),
            ('Yellowstone National Park', '', YELLOWSTONE_DEX_NO, 'Wyoming', '', 'yellowstone', YELLOWSTONE_IMAGE_ROOT_SUFFIX),
        ]

        environment_id = 1
        for name, variant_name, dex_no, location, description, img_root, local_img_suffix in base_environment_data:
            # Add Day variant
            day_environment = (environment_id, name, variant_name, dex_no, 1, location, description, img_root, False, True, 5, local_img_suffix)
            self.queryHandler.execute_query(TGOMMO_INSERT_NEW_ENVIRONMENT, params=day_environment)
            environment_id += 1

            # Add Night variant
            night_environment = (environment_id, name, variant_name, dex_no, 2, location, description, img_root, True, True, 5, local_img_suffix)
            self.queryHandler.execute_query(TGOMMO_INSERT_NEW_ENVIRONMENT, params=night_environment)
            environment_id += 1
    def insert_environment_creature_records(self):
        eastern_us_environment_creature_data = [
            # region EST WAVE 1
            EnvironmentCreatureLink(DEER_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(DEER_DEX_NO, 2, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GRAY_SQUIRREL_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RABBIT_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CHIPMUNK_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RACCOON_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(ROBIN_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SPARROW_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SPARROW_DEX_NO, 2, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BLUEJAY_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GOLDFINCH_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CARDINAL_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(CARDINAL_DEX_NO, 2, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MONARCH_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MONARCH_DEX_NO, 2, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MONARCH_DEX_NO, 3, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MANTIS_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(GARTERSNAKE_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BOXTURTLE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(TOAD_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(MALLARD_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(MALLARD_DEX_NO, 2, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(TURKEY_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(EAGLE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(GREAT_HORNED_OWL_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(OPOSSUM_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(REDFOX_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BOBCAT_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BLACKBEAR_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MOOSE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MOOSE_DEX_NO, 2, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(WOLF_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            # endregion
            # region EST - WAVE 2
            EnvironmentCreatureLink(CAT_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CAT_DEX_NO, 2, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CAT_DEX_NO, 3, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CAT_DEX_NO, 4, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MOUSE_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(GROUNDHOG_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(MOURNING_DOVE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CANADA_GOOSE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(TURKEY_VULTURE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(CICADA_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(CRICKET_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(FIREFLY_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(LUNA_MOTH_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BLACK_WIDOW_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SALAMANDER_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(SNAPPING_TURTLE_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(AMERICAN_CROW_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RED_TAILED_HAWK_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(NIGHTHAWK_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(WOODCOCK_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SCREECH_OWL_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SNOWY_OWL_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BAT_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(FLYING_SQUIRREL_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SKUNK_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(NORTH_AMERICAN_PORCUPINE_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COYOTE_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MOUNTAIN_LION_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_LEGENDARY, 'Cougar', SUB_ENVIRONMENT_FOREST),
            # endregion
            # region EST - WAVE 3
            EnvironmentCreatureLink(SKINK_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COPPERHEAD_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(EARTHWORM_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(EASTERN_MOLE_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(STAR_NOSED_MOLE_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(RED_SQUIRREL_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(THIRTEEN_LINED_GROUND_SQUIRREL_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(STOAT_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BOAR_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(HOUSE_FINCH_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(STARLING_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BLACK_CAPPED_CHICKADEE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BALTIMORE_ORIOLE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(REDWING_BLACKBIRD_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(REDWING_BLACKBIRD_DEX_NO, 2, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(PILEATED_WOODPECKER_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(HUMMINGBIRD_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BARN_SWALLOW_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BARN_OWL_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SNAIL_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SNAIL_DEX_NO, 2, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SNAIL_DEX_NO, 3, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SNAIL_DEX_NO, 4, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SNAIL_DEX_NO, 5, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SNAIL_DEX_NO, 6, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(SNAIL_DEX_NO, 7, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SWALLOWTAIL_BUTTERFLY_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SWALLOWTAIL_BUTTERFLY_DEX_NO, 2, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(TIGER_MOTH_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(POLYPHEMUS_MOTH_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(HONEYBEE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(LADYBUG_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ROLYPOLY_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SPOTTED_LANTERNFLY_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(NORTHERN_WALKING_STICK_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(DRAGONFLY_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(POND_SKATER_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(BULL_FROG_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(BULL_FROG_DEX_NO, 2, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(EASTERN_NEWT_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(CRAYFISH_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(PAINTED_TURTLE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(KILLDEER_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(RING_BILLED_GULL_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(CORMORANT_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(KINGFISHER_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(MUTE_SWAN_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(LOON_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(GREAT_BLUE_HERON_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(BLACK_CROWNED_NIGHT_HERON_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(SANDHILL_CRANE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(MUSKRAT_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(BEAVER_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(RIVER_OTTER_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(HERCULES_BEETLE_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(HERCULES_BEETLE_DEX_NO, 2, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(HELLBENDER_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(PUFFIN_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(HARBOR_SEAL_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(ALLIGATOR_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_RIVER),
            # endregion
            # region EST - WAVE 4
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 2, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 3, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 4, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 5, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 6, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 7, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 8, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 9, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 10, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(FOX_SQUIRREL_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GRAY_FOX_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(EASTERN_PONDHAWK_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(NORTH_AMERICAN_RACER_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(NORTHERN_MOCKINGBIRD_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(PALM_WARBLER_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(YELLOW_RUMPED_WARBLER_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COMMON_GRACKLE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BLACK_VULTURE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(RED_SHOULDERED_HAWK_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(OSPREY_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(GREAT_EGRET_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(ROYAL_TERN_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(BROWN_PELICAN_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(BOTTLE_NOSED_DOLPHIN_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(MOSQUITO_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            # endregion
            # region EST - WAVE 4.5
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 11, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(ROCK_PIGEON_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(BROWN_RAT_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_HORSE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(CARPENTER_ANT_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CARPENTER_ANT_DEX_NO, 2, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(YELLOW_JACKET_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(RED_BANDED_LEAFHOPPER_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(CABBAGE_WHITE_BUTTERFLY_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ORANGE_SULPHUR_BUTTERFLY_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GIANT_WATERBUG_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(JAPANESE_BEETLE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(RED_BACKED_SALAMANDER_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SPRING_PEEPER_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(EASTERN_BLUEBIRD_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GREEN_HERON_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(NORTHERN_BOBWHITE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(RING_NECKED_PHEASANT_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(RING_NECKED_PHEASANT_DEX_NO, 2, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 2, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 3, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 4, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(NORTHERN_SHORT_TAILED_SHREW_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(ELK_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(ELK_DEX_NO, 2, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RED_WOLF_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            # endregion
            # region EST - WAVE 5
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 12, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 13, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),

            EnvironmentCreatureLink(SNOWSHOE_HARE_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(AMERICAN_BADGER_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(FLY_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GOLDEN_DUNG_FLY_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BUMBLEBEE_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BLACK_SLUG_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(WOLF_SPIDER_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(CROSS_ORBWEAVER_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(HARVESTMAN_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(WHITE_LINED_SPHINX_MOTH_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(WHITE_LINED_SPHINX_MOTH_DEX_NO, 2, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SMOOTH_GREENSNAKE_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(LEOPARD_FROG_DEX_NO, 1, EASTERN_US_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(SNOW_BUNTING_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_PIER),
            EnvironmentCreatureLink(COMMON_RAVEN_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(CEDAR_WAXWING_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(NORTHERN_FLICKER_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(TREE_SWALLOW_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(COMMON_EIDER_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(COMMON_EIDER_DEX_NO, 2, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(LONG_TAILED_DUCK_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(COMMON_MERGANSER_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(COMMON_MERGANSER_DEX_NO, 2, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(HOODED_MERGANSER_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(PEREGRINE_FALCON_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GOLDEN_EAGLE_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(ACORN_BARNACLE_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(WHELK_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(MUSSEL_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(COMMON_SEA_STAR_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(GLAUCOUS_GULL_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_PIER),
            EnvironmentCreatureLink(NORTHERN_GANNET_DEX_NO, 1, EASTERN_US_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(RAZORBILL_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(HARBOR_PORPOISE_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(HUMPBACK_WHALE_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_OCEAN),
            # endregion
        ]

        everglades_environment_creature_data = [
            # region FL WAVE 4
            EnvironmentCreatureLink(ALLIGATOR_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP, FL_ALLIGATOR_IMAGE_ROOT),
            EnvironmentCreatureLink(GREEN_ANOLE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CURLY_TAILED_LIZARD_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(EASTERN_GLASS_LIZARD_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(PAINTED_TURTLE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(BOXTURTLE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GOPHER_TORTOISE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SNAPPING_TURTLE_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER, FL_SNAPPING_TURTLE_IMAGE_ROOT),
            EnvironmentCreatureLink(FLORIDA_SOFTSHELL_TURTLE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(NORTH_AMERICAN_RACER_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(GARTERSNAKE_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD, FL_GARTERSNAKE_IMAGE_ROOT),
            EnvironmentCreatureLink(EASTERN_CORALSNAKE_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SQUIRREL_TREEFROG_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BULL_FROG_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND, FL_BULL_FROG_IMAGE_ROOT),
            EnvironmentCreatureLink(BULL_FROG_DEX_NO, 2, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(GREATER_SIREN_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(GRAY_SQUIRREL_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(FOX_SQUIRREL_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST, FL_FOX_SQUIRREL_IMAGE_ROOT),
            EnvironmentCreatureLink(RABBIT_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(EASTERN_MOLE_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DEER_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(DEER_DEX_NO, 2, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(DEER_DEX_NO, 3, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, 'Key Deer', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DEER_DEX_NO, 4, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, 'Key Deer', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(HOUSE_FINCH_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ROBIN_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CARDINAL_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CARDINAL_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(NORTHERN_MOCKINGBIRD_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COMMON_GRACKLE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MOURNING_DOVE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(WHITE_CROWNED_PIGEON_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(PALM_WARBLER_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(YELLOW_RUMPED_WARBLER_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(PAINTED_BUNTING_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(PAINTED_BUNTING_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(HUMMINGBIRD_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BALTIMORE_ORIOLE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BLUEJAY_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(AMERICAN_CROW_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(PILEATED_WOODPECKER_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(TURKEY_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(TURKEY_VULTURE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BLACK_VULTURE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(CRESTED_CARACARA_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(RED_TAILED_HAWK_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(RED_SHOULDERED_HAWK_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(NIGHTHAWK_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SCREECH_OWL_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BARRED_OWL_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BARN_OWL_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BARN_SWALLOW_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SWALLOW_TAILED_KITE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(OSPREY_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(EAGLE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER, FL_EAGLE_IMAGE_ROOT),
            EnvironmentCreatureLink(REDWING_BLACKBIRD_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(REDWING_BLACKBIRD_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(KINGFISHER_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(BLACK_BELLIED_WHISTLING_DUCK_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(PURPLE_GALLINULE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(MOSQUITO_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(MONARCH_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MONARCH_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MONARCH_DEX_NO, 3, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN, FL_MONARCH_IMAGE_ROOT),
            EnvironmentCreatureLink(SWALLOWTAIL_BUTTERFLY_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SWALLOWTAIL_BUTTERFLY_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GULF_FRITILLARY_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GULF_FRITILLARY_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ZEBRA_LONGWING_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ATALA_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(POLYPHEMUS_MOTH_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(DRAGONFLY_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(EASTERN_PONDHAWK_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(LUBBER_GRASSHOPPER_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(HONEYBEE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BUMBLEBEE_MILLIPEDE_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BLACK_WIDOW_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(GOLDEN_ORB_WEAVER_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SPINYBACKED_ORB_WEAVER_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(FIREFLY_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(RACCOON_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD, FL_RACCOON_IMAGE_ROOT),
            EnvironmentCreatureLink(OPOSSUM_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SKUNK_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(NINE_BANDED_ARMADILLO_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(MINK_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RIVER_OTTER_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER, FL_RIVER_OTTER_IMAGE_ROOT),
            EnvironmentCreatureLink(BOBCAT_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COYOTE_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD, FL_COYOTE_IMAGE_ROOT),
            EnvironmentCreatureLink(GRAY_FOX_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST, FL_GRAY_FOX_IMAGE_ROOT),
            EnvironmentCreatureLink(LITTLE_BLUE_HERON_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(GREAT_BLUE_HERON_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER, FL_GREAT_BLUE_HERON_IMAGE_ROOT),
            EnvironmentCreatureLink(BLACK_CROWNED_NIGHT_HERON_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(YELLOW_CROWNED_NIGHT_HERON_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(GREAT_EGRET_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(REDDISH_EGRET_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(WHITE_IBIS_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(CORMORANT_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP, FL_CORMORANT_IMAGE_ROOT),
            EnvironmentCreatureLink(ANHINGA_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(WOOD_STORK_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(SPOONBILL_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(SANDHILL_CRANE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD, FL_SANDHILL_CRANE_IMAGE_ROOT),
            EnvironmentCreatureLink(KILLDEER_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(ROYAL_TERN_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(RING_BILLED_GULL_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(LAUGHING_GULL_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_PIER),
            EnvironmentCreatureLink(BROWN_PELICAN_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_PIER),
            EnvironmentCreatureLink(AMERICAN_WHITE_PELICAN_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(MAGNIFICENT_FRIGATEBIRD_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(MAGNIFICENT_FRIGATEBIRD_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(SNAIL_DEX_NO, 5, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(FLORIDA_TREE_SNAIL_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(CRAYFISH_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(ATLANTIC_GHOST_CRAB_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(ATLANTIC_BLUE_CRAB_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(HORSESHOE_CRAB_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(CONCH_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(CARIBBEAN_LAND_HERMIT_CRAB_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(GREEN_SEA_TURTLE_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(WEST_INDIAN_MANATEE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(BOTTLE_NOSED_DOLPHIN_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(AMERICAN_FLAMINGO_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(BLACKBEAR_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD, FL_BLACKBEAR_IMAGE_ROOT),
            EnvironmentCreatureLink(MOUNTAIN_LION_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_LEGENDARY, 'Panther', SUB_ENVIRONMENT_FIELD, PANTHER_IMAGE_ROOT),
            EnvironmentCreatureLink(AMERICAN_CROCODILE_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_SWAMP),

            EnvironmentCreatureLink(BROWN_ANOLE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(PETERS_ROCK_AGAMA_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(PETERS_ROCK_AGAMA_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GREEN_IGUANA_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(RETICULATED_PYTHON_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(TOKAY_GECKO_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(JACKSONS_CHAMELEON_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(CANE_TOAD_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(LADYBUG_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ROLYPOLY_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SPARROW_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SPARROW_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(STARLING_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(COMMON_MYNA_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_CHICKEN_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_CHICKEN_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_CHICKEN_DEX_NO, 3, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(MUSCOVY_DUCK_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(EGYPTIAN_GOOSE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(INDIAN_PEAFOWL_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(INDIAN_PEAFOWL_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MOUSE_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BOAR_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD, FL_BOAR_IMAGE_ROOT),
            EnvironmentCreatureLink(REDFOX_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST, FL_REDFOX_IMAGE_ROOT),
            EnvironmentCreatureLink(GREEN_MONKEY_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RHESUS_MACAQUE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(CAPYBARA_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 2, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 3, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 4, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 5, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 6, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 7, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 8, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 9, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 10, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_CITY),
            # endregion
            # region FL WAVE 4.5
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 11, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CITY),

            EnvironmentCreatureLink(ROCK_PIGEON_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(BROWN_RAT_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(CARPENTER_ANT_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CARPENTER_ANT_DEX_NO, 2, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(YELLOW_JACKET_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ORANGE_SULPHUR_BUTTERFLY_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CUBAN_TREE_FROG_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(NILE_MONITOR_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(ARGENTINE_BLACK_AND_WHITE_TEGU_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GREEN_HERON_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 3, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 4, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(SCARLET_MACAW_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            # endregion

            # region FL WAVE 4.5
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 11, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CITY),

            EnvironmentCreatureLink(ROCK_PIGEON_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(BROWN_RAT_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(CARPENTER_ANT_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CARPENTER_ANT_DEX_NO, 2, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(YELLOW_JACKET_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ORANGE_SULPHUR_BUTTERFLY_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CUBAN_TREE_FROG_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(NILE_MONITOR_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(ARGENTINE_BLACK_AND_WHITE_TEGU_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GREEN_HERON_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 2, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 3, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(MONK_PARAKEET_DEX_NO, 4, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(SCARLET_MACAW_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            # endregion
            # region FL WAVE 5
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 12, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO, 13, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),

            EnvironmentCreatureLink(FLY_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GOLDEN_DUNG_FLY_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BUMBLEBEE_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(WOLF_SPIDER_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(HARVESTMAN_DEX_NO, 1, FLORIDA_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(NORTHERN_FLICKER_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(TREE_SWALLOW_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(AMERICAN_AVOCET_DEX_NO, 1, FLORIDA_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(HUMPBACK_WHALE_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_OCEAN),
            # endregion

            # endregion

        ]

        iceland_environment_creature_data = [
        ]

        yellowstone_environment_creature_data = [
            EnvironmentCreatureLink(AMERICAN_BISON_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(ELK_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(ELK_DEX_NO, 2, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
             EnvironmentCreatureLink(DEER_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(DEER_DEX_NO, 2, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MOOSE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MOOSE_DEX_NO, 2, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BIGHORN_SHEEP_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CLIFF),
            EnvironmentCreatureLink(MOUNTAIN_GOAT_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CLIFF),
            EnvironmentCreatureLink(PRONGHORN_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DOMESTIC_HORSE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(MOURNING_DOVE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ROBIN_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MOUNTAIN_BLUEBIRD_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(HOUSE_FINCH_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GOLDFINCH_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(LESSER_GOLDFINCH_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GRAY_CROWNED_ROSY_FINCH_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BLACK_CAPPED_CHICKADEE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MOUNTAIN_CHICKADEE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(REDWING_BLACKBIRD_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(REDWING_BLACKBIRD_DEX_NO, 2, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(YELLOW_HEADED_BLACKBIRD_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(CEDAR_WAXWING_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(YELLOW_RUMPED_WARBLER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(COMMON_GRACKLE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(WESTERN_TANAGER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(KINGFISHER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(AMERICAN_DIPPER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(SNOWSHOE_HARE_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(PIKA_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_CLIFF),
            EnvironmentCreatureLink(RACCOON_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RED_SQUIRREL_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(NORTH_AMERICAN_PORCUPINE_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BEAVER_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(HOARY_MARMOT_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BLACK_TAILED_PRAIRIE_DOG_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(WHITE_TAILED_PRAIRIE_DOG_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BLACK_FOOTED_FERRET_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SKUNK_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(STOAT_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RIVER_OTTER_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(PACIFIC_MARTEN_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(AMERICAN_BADGER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BAT_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(ROLYPOLY_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(LADYBUG_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ORNATE_CHECKERED_BEETLE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CARPENTER_ANT_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CARPENTER_ANT_DEX_NO, 2, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MOSQUITO_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(FLY_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GOLDEN_DUNG_FLY_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BUMBLEBEE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CABBAGE_WHITE_BUTTERFLY_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GULF_FRITILLARY_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GULF_FRITILLARY_DEX_NO, 2, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MONARCH_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MONARCH_DEX_NO, 2, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MONARCH_DEX_NO, 3, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(TIGER_MOTH_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(WESTERN_SHEEP_MOTH_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(WHITE_LINED_SPHINX_MOTH_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(WHITE_LINED_SPHINX_MOTH_DEX_NO, 2, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(POND_SKATER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(GIANT_WATERBUG_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(MUSSEL_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(GARTERSNAKE_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(NORTH_AMERICAN_RACER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SMOOTH_GREENSNAKE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SHORT_HORNED_LIZARD_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_DESERT),
            EnvironmentCreatureLink(PRAIRIE_RATTLESNAKE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DESERT_COLLARED_LIZARD_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_DESERT),
            EnvironmentCreatureLink(LEOPARD_FROG_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(WESTERN_TOAD_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(TIGER_SALAMANDER_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MALLARD_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(MALLARD_DEX_NO, 2, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(HARLEQUIN_DUCK_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(SNOW_GOOSE_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(CANADA_GOOSE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(LOON_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(COMMON_MERGANSER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(COMMON_MERGANSER_DEX_NO, 2, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(HOODED_MERGANSER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(WESTERN_GREBE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(GREAT_BLUE_HERON_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(SANDHILL_CRANE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(KILLDEER_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(CORMORANT_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(RING_BILLED_GULL_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(AMERICAN_WHITE_PELICAN_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_PIER),
            EnvironmentCreatureLink(AMERICAN_AVOCET_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(WHITE_FACED_IBIS_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(BLACK_NECKED_STILT_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(STARLING_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MOUSE_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SPARROW_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SPARROW_DEX_NO, 2, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ROCK_PIGEON_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(BROWN_RAT_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(NORTHERN_FLICKER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(LEWIS_WOODPECKER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BLUEJAY_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(STELLARS_JAY_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BLACK_BILLED_MAGPIE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(AMERICAN_CROW_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COMMON_RAVEN_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(CLARKS_NUTCRACKER_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RING_NECKED_PHEASANT_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(RING_NECKED_PHEASANT_DEX_NO, 2, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(TURKEY_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(TURKEY_VULTURE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BARN_SWALLOW_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(TREE_SWALLOW_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(VIOLET_GREEN_SWALLOW_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CLIFF),
            EnvironmentCreatureLink(NIGHTHAWK_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(RED_TAILED_HAWK_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(OSPREY_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(PEREGRINE_FALCON_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(EAGLE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(GREAT_HORNED_OWL_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GOLDEN_EAGLE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(GREAT_GRAY_OWL_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GREATER_SAGE_GROUSE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DUSKY_GROUSE_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(AMERICAN_PRAIRIE_CHICKEN_DEX_NO, 1, YELLOWSTONE_DEX_NO, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(REDFOX_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COYOTE_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(WOLF_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BOBCAT_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MOUNTAIN_LION_DEX_NO, 1, YELLOWSTONE_DEX_NO, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(CANADA_LYNX_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(WOLVERINE_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_CLIFF),
            EnvironmentCreatureLink(BLACKBEAR_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GRIZZLY_BEAR_DEX_NO, 1, YELLOWSTONE_DEX_NO, BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
        ]

        environment_creature_data = [
            eastern_us_environment_creature_data,
            everglades_environment_creature_data,
            iceland_environment_creature_data,
            yellowstone_environment_creature_data,
        ]

        for environment in environment_creature_data:
            previous_ec_link = dummy_ec_link
            for index, ec_link in enumerate(environment):
                creature_info = self.db_handler.get_creature_by_dex_and_variant_no(ec_link.creature_dex_no, ec_link.creature_variant_no)
                environment_info = self.db_handler.get_environments_by_dex_no(dex_no=ec_link.environment_dex_no)

                ec_link.local_dex_no = previous_ec_link.local_dex_no + (1 if not (previous_ec_link and previous_ec_link.creature_dex_no == ec_link.creature_dex_no) else 0)

                spawn_times = []
                if ec_link.spawn_time != NIGHT:
                    spawn_times.append(DAY)
                if ec_link.spawn_time != DAY:
                    spawn_times.append(NIGHT)

                for spawn_time in spawn_times:
                    self.queryHandler.execute_query(TGOMMO_INSERT_ENVIRONMENT_CREATURE, params=_create_environment_creature_params(creature_info, environment_info, spawn_time, ec_link))

                previous_ec_link = ec_link

    def insert_transcendant_environment_creature_records(self):
        eastern_us_environment_creature_data = [
            EnvironmentCreatureLink(BIGFOOT_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FOREST, ),
            EnvironmentCreatureLink(MOTHMAN_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_RIVER, ),
            EnvironmentCreatureLink(FROGMAN_DEX_NO, 1, EASTERN_US_DEX_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_RIVER, ),
        ]
        everglades_environment_creature_data = [
             EnvironmentCreatureLink(BIGFOOT_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FOREST, ),
            EnvironmentCreatureLink(SKUNK_APE_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FOREST, ),
            EnvironmentCreatureLink(CHUPACABRA_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FIELD, ),
            EnvironmentCreatureLink(WAMPUS_CAT_DEX_NO, 1, FLORIDA_DEX_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FIELD, ),
        ]
        environment_creature_data = eastern_us_environment_creature_data + everglades_environment_creature_data
        for ec_link in environment_creature_data:
            creature_info = self.db_handler.get_creature_by_dex_and_variant_no(ec_link.creature_dex_no, ec_link.creature_variant_no)
            environment_info = self.db_handler.get_environments_by_dex_no(dex_no=ec_link.environment_dex_no)

            spawn_times = []
            if ec_link.spawn_time != NIGHT:
                spawn_times.append(DAY)
            if ec_link.spawn_time != DAY:
                spawn_times.append(NIGHT)

            for spawn_time in spawn_times:
                self.queryHandler.execute_query(TGOMMO_INSERT_ENVIRONMENT_CREATURE, params=_create_environment_creature_params(creature_info, environment_info, spawn_time, ec_link))


    def insert_collection_records(self):
        collections_data = [
            (f"{MAMMAL}s", "", f"{DEER_IMAGE_ROOT}_1", MAMMAL, TGOMMO_COLLECTION_QUERY_MAMMAL_TOTAL, TGOMMO_COLLECTION_QUERY_MAMMAL_CAUGHT,  f"{PLAYER_PROFILE_AVATAR_PREFIX}{MAMMAL}_1", f"{PLAYER_PROFILE_AVATAR_PREFIX}{MAMMAL}_2", f"{PLAYER_PROFILE_BACKGROUND_PREFIX}{MAMMAL}_1",  1),
            (f"{BIRD}s", "", f"{BLUEJAY_IMAGE_ROOT}_1", BIRD, TGOMMO_COLLECTION_QUERY_BIRD_TOTAL, TGOMMO_COLLECTION_QUERY_BIRD_CAUGHT, f"{PLAYER_PROFILE_AVATAR_PREFIX}{BIRD}_1", f"{PLAYER_PROFILE_AVATAR_PREFIX}{BIRD}_2", f"{PLAYER_PROFILE_BACKGROUND_PREFIX}{REPTILE}_1",  1),
            (f"{REPTILE}s", "", f"{BOX_TURTLE_IMAGE_ROOT}_1", REPTILE, TGOMMO_COLLECTION_QUERY_REPTILE_TOTAL, TGOMMO_COLLECTION_QUERY_REPTILE_CAUGHT, f"{PLAYER_PROFILE_AVATAR_PREFIX}{REPTILE}_1", f"{PLAYER_PROFILE_AVATAR_PREFIX}{REPTILE}_2", f"{PLAYER_PROFILE_BACKGROUND_PREFIX}{REPTILE}_1", 1),
            (f"{AMPHIBIAN}s", "", f"{TOAD_IMAGE_ROOT}_1", AMPHIBIAN, TGOMMO_COLLECTION_QUERY_AMPHIBIAN_TOTAL, TGOMMO_COLLECTION_QUERY_AMPHIBIAN_CAUGHT, f"{PLAYER_PROFILE_AVATAR_PREFIX}{AMPHIBIAN}_1", f"{PLAYER_PROFILE_BACKGROUND_PREFIX}{AMPHIBIAN}_1", f"{PLAYER_PROFILE_BACKGROUND_PREFIX}{AMPHIBIAN}_2",  1),
            (f"{BUG}s", "", f"{MANTIS_IMAGE_ROOT}_1", BUG, TGOMMO_COLLECTION_QUERY_BUG_TOTAL, TGOMMO_COLLECTION_QUERY_BUG_CAUGHT, f"{PLAYER_PROFILE_AVATAR_PREFIX}{BUG}_1", f"{PLAYER_PROFILE_AVATAR_PREFIX}{BUG}_2", f"{PLAYER_PROFILE_BACKGROUND_PREFIX}{BUG}_1",  1),

            (f"{VARIANTS_COLLECTION_KEYWORD}", "", f"{DEER_IMAGE_ROOT}_2", MAMMAL, TGOMMO_COLLECTION_QUERY_VARIANTS_TOTAL, TGOMMO_COLLECTION_QUERY_VARIANTS_CAUGHT, f"{PLAYER_PROFILE_AVATAR_PREFIX}{VARIANTS_COLLECTION_KEYWORD}_1", f"{PLAYER_PROFILE_AVATAR_PREFIX}{VARIANTS_COLLECTION_KEYWORD}_2", f"{PLAYER_PROFILE_AVATAR_PREFIX}{VARIANTS_COLLECTION_KEYWORD}_3", 1),
        ]

        for index, collection in enumerate(collections_data):
            collection = (index + 1,) + collection
            self.queryHandler.execute_query(TGOMMO_INSERT_COLLECTION, params=collection)

    def insert_item_records(self):
        item_data = [
            # Creature Inventory Storage
            (ITEM_ID_CREATURE_INVENTORY_STORAGE_EXPANSION, 'Creature Storage Upgrade', ITEM_TYPE_GAMEPLAY_MECHANICS, 'Increases your creature storage capacity by 100.', TGOMMO_RARITY_NORMAL, False, '', 1),

            # Name Tags
            (f'{ITEM_TYPE_NAMETAG}_1', 'NameTag', ITEM_TYPE_NAMETAG, 'Lets you rename any creature you already caught', TGOMMO_RARITY_COMMON, False, '', 1, 35),

            # Baits
            (ITEM_ID_BAIT, 'Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch.', TGOMMO_RARITY_NORMAL, True, '', 1, 50),
            (ITEM_ID_COMMON_BAIT, 'Common Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be common.', TGOMMO_RARITY_COMMON, True, '', 1, 35),
            (ITEM_ID_UNCOMMON_BAIT, 'Uncommon Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be uncommon.', TGOMMO_RARITY_UNCOMMON, True, '', 1, 60),
            (ITEM_ID_RARE_BAIT, 'Rare Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be rare.', TGOMMO_RARITY_RARE, True, '', 1, 100),
            (ITEM_ID_EPIC_BAIT, 'Epic Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be epic.', TGOMMO_RARITY_EPIC, True, '', 1, 250),
            (ITEM_ID_LEGENDARY_BAIT, 'Legendary Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be legendary.', TGOMMO_RARITY_LEGENDARY, True, '', 1, 500),
            (ITEM_ID_MYTHICAL_BAIT, 'Mythical Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be mythical.', TGOMMO_RARITY_MYTHICAL, True, '', 1, 500),
            (ITEM_ID_TRANSCENDANT_BAIT, 'Transcendant Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be transcendant.', TGOMMO_RARITY_TRANSCENDANT, False, '', 1, 2500),
            (ITEM_ID_OMNIPOTENT_BAIT, 'Omnipotent Bait', ITEM_TYPE_BAIT, 'Allows you to summon any discovered creature of your choice. Only you can catch this creature.', TGOMMO_RARITY_OMNIPOTENT, False, '', 1, 5000),

            # Megaphones
            (ITEM_TYPE_MEGAPHONE, 'Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a new creature spawns.', TGOMMO_RARITY_NORMAL, False, '', -1, 0),
            (ITEM_ID_COMMON_MEGAPHONE, 'Common Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a common creature spawns.', TGOMMO_RARITY_COMMON, False, '', -1, 250),
            (ITEM_ID_UNCOMMON_MEGAPHONE, 'Uncommon Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a uncommon creature spawns.', TGOMMO_RARITY_UNCOMMON, False, '', -1, 500),
            (ITEM_ID_RARE_MEGAPHONE, 'Rare Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a rare creature spawns.', TGOMMO_RARITY_RARE, False, '', -1, 750),
            (ITEM_ID_EPIC_MEGAPHONE, 'Epic Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever an epic creature spawns.', TGOMMO_RARITY_EPIC, False, '', -1, 1000),
            (ITEM_ID_LEGENDARY_MEGAPHONE, 'Legendary Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a legendary creature spawns.', TGOMMO_RARITY_LEGENDARY, False, '', -1, 2500),
            (ITEM_ID_MYTHICAL_MEGAPHONE, 'Mythical Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a mythical creature spawns.', TGOMMO_RARITY_MYTHICAL, False, '', -1, 10000),
            (ITEM_ID_TRANSCENDANT_MEGAPHONE, 'Transcendant Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a transcendant creature spawns. Breaks after a single catch, though', TGOMMO_RARITY_TRANSCENDANT, False, '', 1, 10000),
            (ITEM_ID_OMNIPOTENT_MEGAPHONE, 'Omnipotent Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you when any creature of your choice spawns. Breaks after a single catch, though.', TGOMMO_RARITY_OMNIPOTENT, False, '', 1, 500),

            # Charms
            (ITEM_ID_CHARM, 'Charm', ITEM_TYPE_CHARM, 'Increases the amount of creatures that will spawn for the next 30 minutes.', TGOMMO_RARITY_NORMAL, True, '', 1, 75),
            (ITEM_ID_COMMON_CHARM, 'Common Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for common creatures. Lasts for 30 minutes', TGOMMO_RARITY_COMMON, True, '', 1, 75),
            (ITEM_ID_UNCOMMON_CHARM, 'Uncommon Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for uncommon creatures. Lasts for 30 minutes', TGOMMO_RARITY_UNCOMMON, True, '', 1, 125),
            (ITEM_ID_RARE_CHARM, 'Rare Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for rare creatures. Lasts for 30 minutes', TGOMMO_RARITY_RARE, True, '', 1, 200),
            (ITEM_ID_EPIC_CHARM, 'Epic Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for epic creatures. Lasts for 30 minutes', TGOMMO_RARITY_EPIC, True, '', 1, 500),
            (ITEM_ID_LEGENDARY_CHARM, 'Legendary Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for legendary creatures. Lasts for 30 minutes', TGOMMO_RARITY_LEGENDARY, True, '', 1, 1000),
            (ITEM_ID_MYTHICAL_CHARM, 'Mythical Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for mythical creatures. Lasts for 30 minutes', TGOMMO_RARITY_MYTHICAL, True, '', 1, 2500),
            (ITEM_ID_TRANSCENDANT_CHARM, 'Transcendant Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for transcendant creatures. Lasts for 30 minutes', TGOMMO_RARITY_TRANSCENDANT, False, '', 1, 10000),
            (ITEM_ID_OMNIPOTENT_CHARM, 'Omnipotent Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for any creature of your choice. Lasts for 10 minutes', TGOMMO_RARITY_OMNIPOTENT, False, '', 1, 10000),
        ]

        for index, item in enumerate(item_data):
            item = (index + 1,) + item
            if len(item) == 9:
                item = item + (0,)

            self.queryHandler.execute_query(TGOMMO_INSERT_NEW_INVENTORY_ITEM, params=item)

    def insert_default_player_records(self):
        self.queryHandler.execute_query(TGOMMO_INSERT_NEW_USER_PROFILE, params=(0, 'Sketching Alley', 'F1', 1, -1, -1, -1, -1, -1, -1, 0, 3, 1, 0,  1, 0))
        self.queryHandler.execute_query(TGOMMO_INSERT_NEW_USER_AVATAR_LINK, params=('F1', 0))


'''HELPER METHODS FOR TGOMMO DATABASE INITIALIZER CLASS BELOW'''
def _create_environment_creature_params(creature_info, environment_info, spawn_time, ec_link):
    """Helper method to create environment creature parameters."""
    env_index = 0 if spawn_time == DAY else 1
    return [
        creature_info.creature_id,
        environment_info[env_index].environment_id,
        spawn_time,
        environment_info[env_index].dex_no,
        environment_info[env_index].variant_no,
        creature_info.creature_name,
        environment_info[env_index].name,
        ec_link.local_rarity,
        ec_link.local_name,
        ec_link.sub_environment,
        ec_link.local_dex_no if ec_link.local_dex_no != 0 else ec_link.creature_dex_no,
        ec_link.local_variant_no if ec_link.local_variant_no != 0 else ec_link.creature_variant_no,
        ec_link.local_img_root
    ]


class EnvironmentCreatureLink:
    def __init__(self, creature_dex_no, creature_variant_no, environment_dex_no, spawn_time, local_rarity, local_name="", sub_environment=SUB_ENVIRONMENT_RIVER, local_img_root="", local_dex_no=0, local_variant_no=0):
        self.creature_dex_no = creature_dex_no
        self.creature_variant_no = creature_variant_no

        self.environment_dex_no = environment_dex_no
        self.spawn_time = spawn_time

        self.local_rarity = local_rarity
        self.local_name = local_name
        self.sub_environment = sub_environment
        self.local_img_root = local_img_root
        self.local_dex_no = local_dex_no
        self.local_variant_no = local_variant_no
dummy_ec_link = EnvironmentCreatureLink(creature_dex_no=0, creature_variant_no=0, environment_dex_no=0, spawn_time="", local_rarity=0, local_name="", sub_environment=SUB_ENVIRONMENT_RIVER, local_img_root="", local_dex_no=0, local_variant_no=0)