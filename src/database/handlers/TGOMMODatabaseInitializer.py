from src.database.handlers.EnvironmentCreatureLink import EnvironmentCreatureLink, dummy_ec_link
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.TGO_MMO_creature_constants import *
from src.resources.constants.queries.avatar_quest_db_queries import *
from src.resources.constants.queries.create_table_queries import *
from src.resources.constants.queries.db_queries import *


class TGOMMODatabaseInitializer:
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
        self.queryHandler.execute_query(TGOMMO_CREATE_COLLECTION_TABLE)
    def clear_old_db_table_data(self):
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_CREATURES, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_ENVIRONMENTS, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_ENVIRONMENT_CREATURES, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_AVATAR_UNLOCK_CONDITIONS, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_COLLECTIONS, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_USER_AVATAR, params=())
        self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_INVENTORY_ITEM, params=())
        # self.queryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_USER_PROFILE_AVATARS, params=())
    def insert_db_table_data(self):
        # insert creature records
        self.insert_creature_records()
        self.insert_transcendant_creature_records()
        
        self.insert_environment_records()
        
        self.insert_user_avatar_records()
        self.insert_user_avatar_unlock_condition_records()
        self.insert_collection_records()
        self.insert_item_records()

        # Link creatures to environments
        self.insert_environment_creature_records()
        self.insert_transcendant_environment_creature_records()

    # ---- INSERT RECORD HELPERS ---- # 
    def insert_creature_records(self):
        creature_data = [
            # WAVE 1
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

            # WAVE 2
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

            # WAVE 3
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
            ('Hellbender', '', 97, 1, 'Hellbender', 'Cryptobranchus alleganiensis', REPTILE, '', HELLBENDER_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Puffin', '', 98, 1, 'Atlantic Puffin', 'Fratercula arctica', BIRD, '', PUFFIN_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Seal', '', 99, 1, 'Harbor Seal', 'Phoca vitulina', MAMMAL, '', HARBOR_SEAL_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Alligator', '', 100, 1, 'American Alligator', 'Alligator mississippiensis', REPTILE, '', ALLIGATOR_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),

            # WAVE 4
            ('Key Deer', 'Doe', 1, 3, 'Key Deer', 'Odocoileus virginianus clavium', MAMMAL, '', DEER_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Key Deer', 'Buck', 1, 4, 'Key Deer', 'Odocoileus virginianus clavium', MAMMAL, '', DEER_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),

            ('Anole', '', 101, 1, 'Green Anole', 'Anolis carolinensis', REPTILE, '', GREEN_ANOLE_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Lizard', '', 102, 1, 'Curly-Tailed Lizard', 'Leiocephalus carinatus', REPTILE, '', CURLY_TAILED_LIZARD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Lizard', '', 103, 1, 'Eastern Glass Lizard', 'Ophisaurus ventralis', REPTILE, '', EASTERN_GLASS_LIZARD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Tortoise', '', 104, 1, 'Gopher Tortoise', 'Gopherus polyphemus', REPTILE, '', GOPHER_TORTOISE_IMAGE_ROOT, 5, TGOMMO_RARITY_EPIC),
            ('Turtle', '', 105, 1, 'Florida Softshell Turtle', 'Apalone ferox', REPTILE, '', FLORIDA_SOFTSHELL_TURTLE_IMAGE_ROOT, 5, TGOMMO_RARITY_LEGENDARY),
            ('Snake', '', 106, 1, 'North American Racer', 'Coluber constrictor', REPTILE, '', NORTH_AMERICAN_RACER_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Snake', '', 107, 1, 'Eastern Coral Snake', 'Micrurus fulvius', REPTILE, '', EASTERN_CORALSNAKE_IMAGE_ROOT, 5, TGOMMO_RARITY_RARE),
            ('TreeFrog', '', 108, 1, 'Florida Treefrog', 'Hyla squirella', AMPHIBIAN, '', SQUIRREL_TREEFROG_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
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
            ('Cane Toad', '', 167, 1, 'Cane Toad', 'Rhinella marina', AMPHIBIAN, '', CANE_TOAD_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
            ('Common Myna', '', 168, 1, 'Common Myna', 'Acridotheres tristis', BIRD, '', COMMON_MYNA_IMAGE_ROOT, 5, TGOMMO_RARITY_COMMON),
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
        # [environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate]
        environment_data = [
            [1, 'Eastern United States', '', 1, 1, 'Eastern United States', '', 'est_us', False, True, 5],
            (2, 'Eastern United States', '',1, 2, 'Eastern United States', '', 'est_us', True, True, 5),
            # 02 Everglades
            (3, 'Everglades National Park', '', 2, 1, 'Florida', '', 'florida', False, True, 5),
            (4, 'Everglades National Park', '', 2, 2, 'Florida', '', 'florida', True, True, 5),
        ]

        for index, environment_details in enumerate(environment_data):
            params = []
            self.queryHandler.execute_query(TGOMMO_INSERT_NEW_ENVIRONMENT, params=environment_details)

    def insert_environment_creature_records(self):
        eastern_us_environment_creature_data = [
            # WAVE 1
            EnvironmentCreatureLink(DEER_DEX_NO,                    1, EASTERN_US_NO,        BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(DEER_DEX_NO,                    2, EASTERN_US_NO,       BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GRAY_SQUIRREL_DEX_NO,   1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RABBIT_DEX_NO,                  1, EASTERN_US_NO,       BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CHIPMUNK_DEX_NO,            1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RACCOON_DEX_NO,             1, EASTERN_US_NO,       NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(ROBIN_DEX_NO,                   1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SPARROW_DEX_NO,             1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SPARROW_DEX_NO,             2, EASTERN_US_NO,      DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BLUEJAY_DEX_NO,             1, EASTERN_US_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GOLDFINCH_DEX_NO,         1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CARDINAL_DEX_NO,            1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(CARDINAL_DEX_NO,            2, EASTERN_US_NO,       DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MONARCH_DEX_NO,           1, EASTERN_US_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MONARCH_DEX_NO,           2, EASTERN_US_NO,       DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MONARCH_DEX_NO,           3, EASTERN_US_NO,       DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MANTIS_DEX_NO,                1, EASTERN_US_NO,        BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(GARTERSNAKE_DEX_NO,     1, EASTERN_US_NO,        BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BOXTURTLE_DEX_NO,           1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(TOAD_DEX_NO,                    1, EASTERN_US_NO,       BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(DUCK_DEX_NO,                    1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(DUCK_DEX_NO,                    2, EASTERN_US_NO,       DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(TURKEY_DEX_NO,                  1, EASTERN_US_NO,      DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(EAGLE_DEX_NO,                   1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(GREAT_HORNED_OWL_DEX_NO, 1, EASTERN_US_NO, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(OPOSSUM_DEX_NO,             1, EASTERN_US_NO,       NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(REDFOX_DEX_NO,                  1, EASTERN_US_NO,      NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BOBCAT_DEX_NO,                  1, EASTERN_US_NO,      NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BLACKBEAR_DEX_NO,           1, EASTERN_US_NO,       BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MOOSE_DEX_NO,                  1, EASTERN_US_NO,      DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MOOSE_DEX_NO,                  2, EASTERN_US_NO,      DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(WOLF_DEX_NO,                    1, EASTERN_US_NO,       NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            # WAVE 2
            EnvironmentCreatureLink(CAT_DEX_NO,                         1, EASTERN_US_NO,       BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CAT_DEX_NO,                         2, EASTERN_US_NO,       BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CAT_DEX_NO,                         3, EASTERN_US_NO,       BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CAT_DEX_NO,                         4, EASTERN_US_NO,       BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MOUSE_DEX_NO,                   1, EASTERN_US_NO,       NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(GROUNDHOG_DEX_NO,           1, EASTERN_US_NO,      DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(MOURNING_DOVE_DEX_NO,   1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CANADA_GOOSE_DEX_NO,     1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(TURKEY_VULTURE_DEX_NO,   1, EASTERN_US_NO,      DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(CICADA_DEX_NO,                    1, EASTERN_US_NO,      DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(CRICKET_DEX_NO,                   1, EASTERN_US_NO,      NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(FIREFLY_DEX_NO,                   1, EASTERN_US_NO,       NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(LUNA_MOTH_DEX_NO,           1, EASTERN_US_NO,       NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BLACK_WIDOW_DEX_NO,         1, EASTERN_US_NO,      NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SALAMANDER_DEX_NO,          1, EASTERN_US_NO,      NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(SNAPPING_TURTLE_DEX_NO, 1, EASTERN_US_NO,       NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(AMERICAN_CROW_DEX_NO,    1, EASTERN_US_NO,      DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RED_TAILED_HAWK_DEX_NO, 1, EASTERN_US_NO,       DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(NIGHTHAWK_DEX_NO,           1, EASTERN_US_NO,       NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(WOODCOCK_DEX_NO,            1, EASTERN_US_NO,       NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SCREECH_OWL_DEX_NO,         1, EASTERN_US_NO,      NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SNOWY_OWL_DEX_NO,         1, EASTERN_US_NO,        DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BAT_DEX_NO,                         1, EASTERN_US_NO,       NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(FLYING_SQUIRREL_DEX_NO, 1, EASTERN_US_NO,         NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SKUNK_DEX_NO,                   1, EASTERN_US_NO,         NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(PORCUPINE_DEX_NO,           1, EASTERN_US_NO,         NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COYOTE_DEX_NO,                1, EASTERN_US_NO,         NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(MOUNTAIN_LION_DEX_NO, 1, EASTERN_US_NO,          NIGHT, TGOMMO_RARITY_LEGENDARY, 'Cougar', SUB_ENVIRONMENT_FOREST),
            # WAVE 3
            EnvironmentCreatureLink(SKINK_DEX_NO,                                                      1, EASTERN_US_NO,        BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COPPERHEAD_DEX_NO,                                         1, EASTERN_US_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(EARTHWORM_DEX_NO,                                         1, EASTERN_US_NO,         NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(EASTERN_MOLE_DEX_NO,                                    1, EASTERN_US_NO,          NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(STAR_NOSED_MOLE_DEX_NO,                             1, EASTERN_US_NO,           NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(RED_SQUIRREL_DEX_NO,                                       1, EASTERN_US_NO,         DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(THIRTEEN_LINED_GROUND_SQUIRREL_DEX_NO,  1, EASTERN_US_NO,          DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(STOAT_DEX_NO,                                                   1, EASTERN_US_NO,         NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BOAR_DEX_NO,                                                    1, EASTERN_US_NO,          NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(HOUSE_FINCH_DEX_NO,                                     1, EASTERN_US_NO,           DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(STARLING_DEX_NO,                                            1, EASTERN_US_NO,           DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BLACK_CAPPED_CHICKADEE_DEX_NO,                1, EASTERN_US_NO,           DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BALTIMORE_ORIOLE_DEX_NO,                            1, EASTERN_US_NO,            DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(REDWING_BLACKBIRD_DEX_NO,                          1, EASTERN_US_NO,           DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(REDWING_BLACKBIRD_DEX_NO,                           2, EASTERN_US_NO,          DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(PILEATED_WOODPECKER_DEX_NO,                     1, EASTERN_US_NO,           DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(HUMMINGBIRD_DEX_NO,                                     1, EASTERN_US_NO,          DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BARN_SWALLOW_DEX_NO,                                  1, EASTERN_US_NO,          NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BARN_OWL_DEX_NO,                                            1, EASTERN_US_NO,         NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SNAIL_DEX_NO,                                                    1, EASTERN_US_NO,          BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SNAIL_DEX_NO,                                                   2, EASTERN_US_NO,           NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SNAIL_DEX_NO,                                                   3, EASTERN_US_NO,           NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SNAIL_DEX_NO,                                                   4, EASTERN_US_NO,           NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SNAIL_DEX_NO,                                                   5, EASTERN_US_NO,           NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SNAIL_DEX_NO,                                                   6, EASTERN_US_NO,           NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(SNAIL_DEX_NO,                                                   7, EASTERN_US_NO,           BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SWALLOWTAIL_BUTTERFLY_DEX_NO,                 1, EASTERN_US_NO,            DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SWALLOWTAIL_BUTTERFLY_DEX_NO,                 2, EASTERN_US_NO,           DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(TIGER_MOTH_DEX_NO,                                      1, EASTERN_US_NO,             NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(POLYPHEMUS_MOTH_DEX_NO,                         1, EASTERN_US_NO,             NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(HONEYBEE_DEX_NO,                                         1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(LADYBUG_DEX_NO,                                           1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ROLYPOLY_DEX_NO,                                        1, EASTERN_US_NO,               NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SPOTTED_LANTERNFLY_DEX_NO,                    1, EASTERN_US_NO,               BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(NORTHERN_WALKING_STICK_DEX_NO,             1, EASTERN_US_NO,              NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(DRAGONFLY_DEX_NO,                                      1, EASTERN_US_NO,              DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(POND_SKATER_DEX_NO,                                 1, EASTERN_US_NO,                DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(BULL_FROG_DEX_NO,                                      1, EASTERN_US_NO,               BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(BULL_FROG_DEX_NO,                                      2, EASTERN_US_NO,               NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(EASTERN_NEWT_DEX_NO,                               1, EASTERN_US_NO,               NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(CRAYFISH_DEX_NO,                                        1, EASTERN_US_NO,               NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(PAINTED_TURTLE_DEX_NO,                             1, EASTERN_US_NO,              DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(KILLDEER_DEX_NO,                                          1, EASTERN_US_NO,              NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(SEAGULL_DEX_NO,                                         1, EASTERN_US_NO,               DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(CORMORANT_DEX_NO,                                   1, EASTERN_US_NO,               DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(KINGFISHER_DEX_NO,                                      1, EASTERN_US_NO,              DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(MUTE_SWAN_DEX_NO,                                   1, EASTERN_US_NO,               DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(LOON_DEX_NO,                                                1, EASTERN_US_NO,             NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(GREAT_BLUE_HERON_DEX_NO,                        1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(BLACK_CROWNED_NIGHT_HERON_DEX_NO,   1, EASTERN_US_NO,               NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(SANDHILL_CRANE_DEX_NO,                            1, EASTERN_US_NO,              DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(MUSKRAT_DEX_NO,                                         1, EASTERN_US_NO,              NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(BEAVER_DEX_NO,                                              1, EASTERN_US_NO,            NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(RIVER_OTTER_DEX_NO,                                     1, EASTERN_US_NO,             BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(HERCULES_BEETLE_DEX_NO,                             1, EASTERN_US_NO,            BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(HERCULES_BEETLE_DEX_NO,                             2, EASTERN_US_NO,           BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(HELLBENDER_DEX_NO,                                      1, EASTERN_US_NO,            NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(PUFFIN_DEX_NO,                                              1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(HARBOR_SEAL_DEX_NO,                                   1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(ALLIGATOR_DEX_NO,                                        1, EASTERN_US_NO,             BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_RIVER),
            # WAVE 4
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          1, EASTERN_US_NO,             BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          2, EASTERN_US_NO,             BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          3, EASTERN_US_NO,             BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          4, EASTERN_US_NO,             BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          5, EASTERN_US_NO,             BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          6, EASTERN_US_NO,             BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          7, EASTERN_US_NO,             BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          8, EASTERN_US_NO,             BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          9, EASTERN_US_NO,             BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          10, EASTERN_US_NO,           BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(FOX_SQUIRREL_DEX_NO,                            1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GRAY_FOX_DEX_NO,                                   1, EASTERN_US_NO,            NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(EASTERN_PONDHAWK_DEX_NO,                1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(NORTH_AMERICAN_RACER_DEX_NO,         1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(NORTHERN_MOCKINGBIRD_DEX_NO,         1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(PALM_WARBLER_DEX_NO,                          1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(YELLOW_RUMPED_WARBLER_DEX_NO,      1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COMMON_GRACKLE_DEX_NO,                   1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BLACK_VULTURE_DEX_NO,                         1, EASTERN_US_NO,            DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(RED_SHOULDERED_HAWK_DEX_NO,           1, EASTERN_US_NO,            DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(OSPREY_DEX_NO,                                       1, EASTERN_US_NO,            DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(GREAT_EGRET_DEX_NO,                             1, EASTERN_US_NO,            DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(ROYAL_TERN_DEX_NO,                               1, EASTERN_US_NO,            DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(BROWN_PELICAN_DEX_NO,                        1, EASTERN_US_NO,             DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(BOTTLE_NOSED_DOLPHIN_DEX_NO,           1, EASTERN_US_NO,            BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_OCEAN),
        ]

        everglades_environment_creature_data = [
            EnvironmentCreatureLink(ALLIGATOR_DEX_NO,                                  1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP,                         FL_ALLIGATOR_IMAGE_ROOT),
            EnvironmentCreatureLink(GREEN_ANOLE_DEX_NO,                            1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CURLY_TAILED_LIZARD_DEX_NO,                1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(EASTERN_GLASS_LIZARD_DEX_NO,            1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(PAINTED_TURTLE_DEX_NO,                        1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(BOXTURTLE_DEX_NO,                                 1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(GOPHER_TORTOISE_DEX_NO,                     1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SNAPPING_TURTLE_DEX_NO,                     1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER,                        FL_SNAPPING_TURTLE_IMAGE_ROOT),
            EnvironmentCreatureLink(FLORIDA_SOFTSHELL_TURTLE_DEX_NO,    1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(NORTH_AMERICAN_RACER_DEX_NO,         1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(GARTERSNAKE_DEX_NO,                            1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD,                         FL_GARTERSNAKE_IMAGE_ROOT),
            EnvironmentCreatureLink(EASTERN_CORALSNAKE_DEX_NO,              1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SQUIRREL_TREEFROG_DEX_NO,                 1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BULL_FROG_DEX_NO,                                 1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND,                          FL_BULL_FROG_IMAGE_ROOT),
            EnvironmentCreatureLink(BULL_FROG_DEX_NO,                                 2, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(GREATER_SIREN_DEX_NO,                          1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(GRAY_SQUIRREL_DEX_NO,                         1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(FOX_SQUIRREL_DEX_NO,                            1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST,                        FL_FOX_SQUIRREL_IMAGE_ROOT),
            EnvironmentCreatureLink(RABBIT_DEX_NO,                                         1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(EASTERN_MOLE_DEX_NO,                          1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DEER_DEX_NO,                                           1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(DEER_DEX_NO,                                           2, FLORIDA_NO,        BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(DEER_DEX_NO,                                           3, FLORIDA_NO,        BOTH, TGOMMO_RARITY_EPIC, 'Key Deer', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(DEER_DEX_NO,                                           4, FLORIDA_NO,        BOTH, TGOMMO_RARITY_EPIC, 'Key Deer', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(HOUSE_FINCH_DEX_NO,                            1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ROBIN_DEX_NO,                                          1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CARDINAL_DEX_NO,                                    1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(CARDINAL_DEX_NO,                                    2, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(NORTHERN_MOCKINGBIRD_DEX_NO,          1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COMMON_GRACKLE_DEX_NO,                    1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MOURNING_DOVE_DEX_NO,                       1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(WHITE_CROWNED_PIGEON_DEX_NO,          1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(PALM_WARBLER_DEX_NO,                          1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(YELLOW_RUMPED_WARBLER_DEX_NO,       1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(PAINTED_BUNTING_DEX_NO,                     1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(PAINTED_BUNTING_DEX_NO,                      2, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(HUMMINGBIRD_DEX_NO,                            1, FLORIDA_NO,        DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BALTIMORE_ORIOLE_DEX_NO,                    1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(BLUEJAY_DEX_NO,                                     1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(AMERICAN_CROW_DEX_NO,                       1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(PILEATED_WOODPECKER_DEX_NO,            1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(TURKEY_DEX_NO,                                       1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(TURKEY_VULTURE_DEX_NO,                      1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BLACK_VULTURE_DEX_NO,                         1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(CRESTED_CARACARA_DEX_NO,                  1, FLORIDA_NO,        DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(RED_TAILED_HAWK_DEX_NO,                      1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(RED_SHOULDERED_HAWK_DEX_NO,           1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(NIGHTHAWK_DEX_NO,                                1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SCREECH_OWL_DEX_NO,                            1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BARRED_OWL_DEX_NO,                              1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BARN_OWL_DEX_NO,                                  1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BARN_SWALLOW_DEX_NO,                         1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(SWALLOW_TAILED_KITE_DEX_NO,              1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(OSPREY_DEX_NO,                                       1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(EAGLE_DEX_NO,                                         1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER,                              FL_EAGLE_IMAGE_ROOT),
            EnvironmentCreatureLink(REDWING_BLACKBIRD_DEX_NO,                  1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(REDWING_BLACKBIRD_DEX_NO,                  2, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(KINGFISHER_DEX_NO,                                 1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(BLACK_BELLIED_WHISTLING_DUCK_DEX_NO,1, FLORIDA_NO,      DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(PURPLE_GALLINULE_DEX_NO,                    1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(MOSQUITO_DEX_NO,                                  1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(MONARCH_DEX_NO,                                   1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MONARCH_DEX_NO,                                   2, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MONARCH_DEX_NO,                                   3, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN,                              FL_MONARCH_IMAGE_ROOT),
            EnvironmentCreatureLink(SWALLOWTAIL_BUTTERFLY_DEX_NO,         1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SWALLOWTAIL_BUTTERFLY_DEX_NO,         2, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GULF_FRITILLARY_DEX_NO,                        1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GULF_FRITILLARY_DEX_NO,                        2, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ZEBRA_LONGWING_DEX_NO,                      1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ATALA_DEX_NO,                                         1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(POLYPHEMUS_MOTH_DEX_NO,                 1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(DRAGONFLY_DEX_NO,                               1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(EASTERN_PONDHAWK_DEX_NO,                 1, FLORIDA_NO,       DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(LUBBER_GRASSHOPPER_DEX_NO,              1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(HONEYBEE_DEX_NO,                                  1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(BUMBLEBEE_MILLIPEDE_DEX_NO,              1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(BLACK_WIDOW_DEX_NO,                            1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(GOLDEN_ORB_WEAVER_DEX_NO,               1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SPINYBACKED_ORB_WEAVER_DEX_NO,      1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(FIREFLY_DEX_NO,                                      1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(RACCOON_DEX_NO,                                   1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_EPIC, '',          SUB_ENVIRONMENT_FIELD,                                FL_RACCOON_IMAGE_ROOT),
            EnvironmentCreatureLink(OPOSSUM_DEX_NO,                                   1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(SKUNK_DEX_NO,                                         1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(NINE_BANDED_ARMADILLO_DEX_NO,          1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(MINK_DEX_NO,                                            1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RIVER_OTTER_DEX_NO,                              1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER,                               FL_RIVER_OTTER_IMAGE_ROOT),
            EnvironmentCreatureLink(BOBCAT_DEX_NO,                                      1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(COYOTE_DEX_NO,                                      1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD,                              FL_COYOTE_IMAGE_ROOT),
            EnvironmentCreatureLink(GRAY_FOX_DEX_NO,                                  1, FLORIDA_NO,        DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST,                              FL_GRAY_FOX_IMAGE_ROOT),
            EnvironmentCreatureLink(LITTLE_BLUE_HERON_DEX_NO,                  1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(GREAT_BLUE_HERON_DEX_NO,                  1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER,                             FL_GREAT_BLUE_HERON_IMAGE_ROOT),
            EnvironmentCreatureLink(BLACK_CROWNED_NIGHT_HERON_DEX_NO,1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(YELLOW_CROWNED_NIGHT_HERON_DEX_NO,1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(GREAT_EGRET_DEX_NO,                             1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(REDDISH_EGRET_DEX_NO,                          1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(WHITE_IBIS_DEX_NO,                                  1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(CORMORANT_DEX_NO,                              1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_SWAMP,                            FL_CORMORANT_IMAGE_ROOT),
            EnvironmentCreatureLink(ANHINGA_DEX_NO,                                    1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(WOOD_STORK_DEX_NO,                             1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(SPOONBILL_DEX_NO,                                 1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(SANDHILL_CRANE_DEX_NO,                       1, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD,                             FL_SANDHILL_CRANE_IMAGE_ROOT),
            EnvironmentCreatureLink(KILLDEER_DEX_NO,                                     1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(ROYAL_TERN_DEX_NO,                               1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(SEAGULL_DEX_NO,                                     1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(LAUGHING_GULL_DEX_NO,                        1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_PIER),
            EnvironmentCreatureLink(BROWN_PELICAN_DEX_NO,                        1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_PIER),
            EnvironmentCreatureLink(AMERICAN_WHITE_PELICAN_DEX_NO,        1, FLORIDA_NO,        DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(MAGNIFICENT_FRIGATEBIRD_DEX_NO,       1, FLORIDA_NO,        DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(MAGNIFICENT_FRIGATEBIRD_DEX_NO,       2, FLORIDA_NO,        DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(SNAIL_DEX_NO,                                          5, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(FLORIDA_TREE_SNAIL_DEX_NO,                  1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(CRAYFISH_DEX_NO,                                   1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(ATLANTIC_GHOST_CRAB_DEX_NO,             1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(ATLANTIC_BLUE_CRAB_DEX_NO,                1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(HORSESHOE_CRAB_DEX_NO,                     1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(CONCH_DEX_NO,                                       1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(CARIBBEAN_LAND_HERMIT_CRAB_DEX_NO,1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(GREEN_SEA_TURTLE_DEX_NO,                   1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(WEST_INDIAN_MANATEE_DEX_NO,             1, FLORIDA_NO,        DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(BOTTLE_NOSED_DOLPHIN_DEX_NO,           1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_OCEAN),
            EnvironmentCreatureLink(AMERICAN_FLAMINGO_DEX_NO,                1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_BEACH),
            EnvironmentCreatureLink(BLACKBEAR_DEX_NO,                                 1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD,                        FL_BLACKBEAR_IMAGE_ROOT),
            EnvironmentCreatureLink(MOUNTAIN_LION_DEX_NO,                         1, FLORIDA_NO,        NIGHT, TGOMMO_RARITY_LEGENDARY, 'Panther', SUB_ENVIRONMENT_FIELD,           PANTHER_IMAGE_ROOT),
            EnvironmentCreatureLink(AMERICAN_CROCODILE_DEX_NO,               1, FLORIDA_NO,        BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_SWAMP),

            EnvironmentCreatureLink(BROWN_ANOLE_DEX_NO,                           1, FLORIDA_NO,            DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(PETERS_ROCK_AGAMA_DEX_NO,               1, FLORIDA_NO,          DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(PETERS_ROCK_AGAMA_DEX_NO,               2, FLORIDA_NO,          DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(GREEN_IGUANA_DEX_NO,                          1, FLORIDA_NO,            DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(RETICULATED_PYTHON_DEX_NO,              1, FLORIDA_NO,           NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(TOKAY_GECKO_DEX_NO,                           1, FLORIDA_NO,           NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(JACKSONS_CHAMELEON_DEX_NO,            1, FLORIDA_NO,          NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(CANE_TOAD_DEX_NO,                                1, FLORIDA_NO,          NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(LADYBUG_DEX_NO,                                    1, FLORIDA_NO,          DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(ROLYPOLY_DEX_NO,                                  1, FLORIDA_NO,          NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SPARROW_DEX_NO,                                    1, FLORIDA_NO,          DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(SPARROW_DEX_NO,                                    2, FLORIDA_NO,         DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(STARLING_DEX_NO,                                    1, FLORIDA_NO,          DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(COMMON_MYNA_DEX_NO,                        1, FLORIDA_NO,           DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_CHICKEN_DEX_NO,                   1, FLORIDA_NO,           DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_CHICKEN_DEX_NO,                   2, FLORIDA_NO,           DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_CHICKEN_DEX_NO,                   3, FLORIDA_NO,           DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(MUSCOVY_DUCK_DEX_NO,                        1, FLORIDA_NO,            DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(EGYPTIAN_GOOSE_DEX_NO,                      1, FLORIDA_NO,            DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            EnvironmentCreatureLink(INDIAN_PEAFOWL_DEX_NO,                       1, FLORIDA_NO,            DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(INDIAN_PEAFOWL_DEX_NO,                       2, FLORIDA_NO,            DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            EnvironmentCreatureLink(MOUSE_DEX_NO,                                       1, FLORIDA_NO,             NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            EnvironmentCreatureLink(BOAR_DEX_NO,                                           1, FLORIDA_NO,            NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD,                             FL_BOAR_IMAGE_ROOT),
            EnvironmentCreatureLink(REDFOX_DEX_NO,                                       1, FLORIDA_NO,            NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST,                        FL_REDFOX_IMAGE_ROOT),
            EnvironmentCreatureLink(GREEN_MONKEY_DEX_NO,                         1, FLORIDA_NO,            DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            EnvironmentCreatureLink(RHESUS_MACAQUE_DEX_NO,                    1, FLORIDA_NO,            DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_RIVER),
            EnvironmentCreatureLink(CAPYBARA_DEX_NO,                                  1, FLORIDA_NO,            NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_SWAMP),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          1, FLORIDA_NO,            BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          2, FLORIDA_NO,            BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          3, FLORIDA_NO,            BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          4, FLORIDA_NO,            BOTH, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          5, FLORIDA_NO,            BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          6, FLORIDA_NO,            BOTH, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          7, FLORIDA_NO,            BOTH, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          8, FLORIDA_NO,            BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          9, FLORIDA_NO,            BOTH, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_CITY),
            EnvironmentCreatureLink(DOMESTIC_DOG_DEX_NO,                          10, FLORIDA_NO,           BOTH, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_CITY),


        ]

        environment_creature_data = [
            eastern_us_environment_creature_data,
            everglades_environment_creature_data
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
            EnvironmentCreatureLink(BIGFOOT_DEX_NO, 1, EASTERN_US_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FOREST, ),
            EnvironmentCreatureLink(MOTHMAN_DEX_NO, 1, EASTERN_US_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_RIVER, ),
            EnvironmentCreatureLink(FROGMAN_DEX_NO, 1, EASTERN_US_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_RIVER,),
        ]
        everglades_environment_creature_data = [
             EnvironmentCreatureLink(BIGFOOT_DEX_NO, 1, FLORIDA_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FOREST, ),
            EnvironmentCreatureLink(SKUNK_APE_DEX_NO, 1, FLORIDA_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FOREST, ),
            EnvironmentCreatureLink(CHUPACABRA_DEX_NO, 1, FLORIDA_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FIELD, ),
            EnvironmentCreatureLink(WAMPUS_CAT_DEX_NO, 1, FLORIDA_NO, BOTH, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FIELD, ),
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

            (f"{VARIANTS}", "", f"{DEER_IMAGE_ROOT}_2", MAMMAL, TGOMMO_COLLECTION_QUERY_VARIANTS_TOTAL, TGOMMO_COLLECTION_QUERY_VARIANTS_CAUGHT, f"{PLAYER_PROFILE_AVATAR_PREFIX}{VARIANTS}_1", f"{PLAYER_PROFILE_AVATAR_PREFIX}{VARIANTS}_2", f"{PLAYER_PROFILE_AVATAR_PREFIX}{VARIANTS}_3", 1),
        ]

        for index, collection in enumerate(collections_data):
            collection = (index + 1,) + collection
            self.queryHandler.execute_query(TGOMMO_INSERT_COLLECTION, params=collection)

    def insert_user_avatar_records(self):
        avatar_data = [
            # ----DEFAULT AVATARS----
            ('D1', 'Red', AVATAR_TYPE_DEFAULT, 'Red', 'Pokemon',),
            ('D2', 'Leaf', AVATAR_TYPE_DEFAULT, 'Leaf', 'Pokemon',),
            ('D3', 'Hilbert', AVATAR_TYPE_DEFAULT, 'Hilbert', 'Pokemon',),
            ('D4', 'Hilda', AVATAR_TYPE_DEFAULT, 'Hilda', 'Pokemon',),
            ('D5', 'Paxton', AVATAR_TYPE_DEFAULT, 'Paxton', 'Pokemon',),
            ('D6', 'Harmony', AVATAR_TYPE_DEFAULT, 'Harmony', 'Pokemon',),
            ('D7', 'Brendan', AVATAR_TYPE_DEFAULT, 'Brendan', 'Pokemon',),
            ('D8', 'May', AVATAR_TYPE_DEFAULT, 'May', 'Pokemon',),

            # ----SECRET AVATARS----
            # WAVE 1
            ('S1', 'Jordo', AVATAR_TYPE_SECRET, 'Jordo', 'Sketching Alley',),
            ('S2', 'Miku', AVATAR_TYPE_SECRET, 'Miku', 'Vocaloid',),
            ('S3', 'Garfield', AVATAR_TYPE_SECRET, 'Garfield', 'Garfield',),
            ('S4', 'Samus', AVATAR_TYPE_SECRET, 'Samus', 'Metroid',),
            ('S5', 'Boss Baby', AVATAR_TYPE_SECRET, 'BossBaby', 'Boss Baby',),
            ('S6', 'Walter White', AVATAR_TYPE_SECRET, 'WalterWhite', 'Breaking Bad',),
            # WAVE 2
            ('S7', 'Jesse Pinkman', AVATAR_TYPE_SECRET, 'JessePinkman', 'Breaking Bad',),
            ('S8', 'Mike Ehrmantraut', AVATAR_TYPE_SECRET, 'MikeEhrmantraut', 'Breaking Bad',),
            ('S9', 'Porky Pig', AVATAR_TYPE_SECRET, 'Porky', 'Looney Tunes',),
            ('S10', 'Jason Vorhees', AVATAR_TYPE_SECRET, 'JasonVorhees', 'Friday the 13th',),

            # Event Avatars
            ('E1', 'Pim', AVATAR_TYPE_EVENT, 'Pim', 'Smiling Friends',),
            ('E2', 'Charlie', AVATAR_TYPE_EVENT, 'Charlie', 'Smiling Friends',),
            ('E3', 'Freddy Fazbear', AVATAR_TYPE_EVENT, 'FreddyFazbear', 'Five Nights at Freddy\'s',),
            ('E4', 'Allan', AVATAR_TYPE_EVENT, 'Allan', 'Smiling Friends',),
            ('E5', 'Glep', AVATAR_TYPE_EVENT, 'Glep', 'Smiling Friends',),
            ('E6', 'The Boss', AVATAR_TYPE_EVENT, 'TheBoss', 'Smiling Friends',),
            ('E7', 'Mr. Frog', AVATAR_TYPE_EVENT, 'MrFrog', 'Smiling Friends',),
            ('E8', 'Tyler', AVATAR_TYPE_EVENT, 'Tyler', 'Smiling Friends',),
            ('E9', 'Smormu', AVATAR_TYPE_EVENT, 'Smormu', 'Smiling Friends',),
            ('E10', 'Blue Janitor Dude', AVATAR_TYPE_EVENT, 'BlueJanitorDude', 'Smiling Friends',),
            ('E11', 'Dolly Dimpley', AVATAR_TYPE_EVENT, 'DollyDimpley', 'Smiling Friends',),
            ('E12', 'Cool Autistic Gamer 774', AVATAR_TYPE_EVENT, 'CoolAutisticGamer774', 'Smiling Friends',),
            # WAVE 2
            ('E13', 'Yuji Itadori', AVATAR_TYPE_EVENT, 'YujiItadori', 'Jujutsu Kaisen',),
            ('E14', 'Megumi Fushiguro', AVATAR_TYPE_EVENT, 'MegumiFushiguro', 'Jujutsu Kaisen',),
            ('E15', 'Nobara Kugisaki', AVATAR_TYPE_EVENT, 'NobaraKugisaki', 'Jujutsu Kaisen',),
            ('E16', 'Satoru Gojo', AVATAR_TYPE_EVENT, 'SatoruGojo', 'Jujutsu Kaisen',),
            ('E17', 'Kento Nanami', AVATAR_TYPE_EVENT, 'KentoNanami', 'Jujutsu Kaisen',),
            ('E18', 'Maki Zen\'in', AVATAR_TYPE_EVENT, 'MakiZenin', 'Jujutsu Kaisen',),
            ('E19', 'Suguru Geto', AVATAR_TYPE_EVENT, 'SuguruGeto', 'Jujutsu Kaisen',),
            ('E20', 'Toji Fushiguro', AVATAR_TYPE_EVENT, 'TojiFushiguro', 'Jujutsu Kaisen',),
            ('E21', 'Mahito', AVATAR_TYPE_EVENT, 'Mahito', 'Jujutsu Kaisen',),
            ('E22', 'Panda', AVATAR_TYPE_EVENT, 'Panda', 'Jujutsu Kaisen',),
            ('E23', 'Jogo', AVATAR_TYPE_EVENT, 'Jogo', 'Jujutsu Kaisen',),
            ('E24', 'Ryomen Sukuna', AVATAR_TYPE_EVENT, 'RyomenSukuna', 'Jujutsu Kaisen',),

            # ----QUEST AVATARS----
            #  COLLECTIONS
            ('Q1', 'Donkey Kong', AVATAR_TYPE_QUEST, 'DonkeyKong', 'Donkey Kong Country',),
            ('Q2', 'Big Bird', AVATAR_TYPE_QUEST, 'BigBird', 'Sesame Street',),
            ('Q3', 'Gex', AVATAR_TYPE_QUEST, 'Gex', 'Gex',),
            ('Q4', 'Kermit', AVATAR_TYPE_QUEST, 'Kermit', 'Muppets',),
            ('Q5', 'Hornet', AVATAR_TYPE_QUEST, 'Hornet', 'Hollow Knight',),
            ('Q6', 'TMNT', AVATAR_TYPE_QUEST, 'TMNT', 'Teenage Mutant Ninja Turtles', True,),
            ('Q6a', 'Leonardo', AVATAR_TYPE_QUEST, 'Leonardo', 'Teenage Mutant Ninja Turtles',),
            ('Q6b', 'Raphael', AVATAR_TYPE_QUEST, 'Raphael', 'Teenage Mutant Ninja Turtles',),
            ('Q6c', 'Michelangelo', AVATAR_TYPE_QUEST, 'Michelangelo', 'Teenage Mutant Ninja Turtles',),
            ('Q6d', 'Donatello', AVATAR_TYPE_QUEST, 'Donatello', 'Teenage Mutant Ninja Turtles',),
            # WAVE 1
            ('Q7', 'HeartGold/ SoulSilver Protagonists', AVATAR_TYPE_QUEST, 'HGSS', 'Pokemon', True,),
            ('Q7a', 'Ethan', AVATAR_TYPE_QUEST, 'Ethan', 'Pokemon',),
            ('Q7b', 'Lyra', AVATAR_TYPE_QUEST, 'Lyra', 'Pokemon',),
            ('Q8', 'Homer', AVATAR_TYPE_QUEST, 'Homer', 'The Simpsons',),
            # WAVE 2
            ('Q9', 'Turbo Granny', AVATAR_TYPE_QUEST, 'TurboGranny', 'DanDaDan',),
            ('Q10', 'Mordecai', AVATAR_TYPE_QUEST, 'Mordecai', 'Regular Show',),
            ('Q11', 'Rigby', AVATAR_TYPE_QUEST, 'Rigby', 'Regular Show',),
            ('Q12', 'Squirrel Girl', AVATAR_TYPE_QUEST, 'SquirrelGirl', 'Marvel',),
            ('Q13', 'Noko Shikanoko', AVATAR_TYPE_QUEST, 'NokoShikanoko', 'Anime',),
            ('Q14', 'Huntrix', AVATAR_TYPE_QUEST, 'Huntrix', 'K-Pop Demon Hunters',  True,),
            ('Q14a', 'Rumi', AVATAR_TYPE_QUEST, 'Rumi', 'K-Pop Demon Hunters',),
            ('Q14b', 'Mira', AVATAR_TYPE_QUEST, 'Mira', 'K-Pop Demon Hunters',),
            ('Q14c', 'Zoey', AVATAR_TYPE_QUEST, 'Zoey', 'K-Pop Demon Hunters',),
            ('Q15', 'Shuma Gorath', AVATAR_TYPE_QUEST, 'ShumaGorath', 'Marvel',),
            ('Q16', 'Gary', AVATAR_TYPE_QUEST, 'Gary', 'Pokemon',),
            # WAVE 3
            ('Q17', 'Bugs Bunny', AVATAR_TYPE_QUEST, 'Bugs', 'Looney Tunes',),
            ('Q18', 'Daffy Duck', AVATAR_TYPE_QUEST, 'Daffy', 'Looney Tunes',),
            ('Q19', 'Puss In Boots', AVATAR_TYPE_QUEST, 'PussInBoots', 'Shrek',),
            ('Q20', 'Bubsy', AVATAR_TYPE_QUEST, 'Bubsy', 'Bubsy',),
            ('Q21', 'Spider-Man', AVATAR_TYPE_QUEST, 'SpiderMan', 'Marvel',),
            ('Q22', 'Cynthia', AVATAR_TYPE_QUEST, 'Cynthia', 'Pokemon',),
            ('Q23', 'Marceline', AVATAR_TYPE_QUEST, 'Marceline', 'Adventure Time',),
            # WAVE 4


            # Transcendant Avatars
            ('T1', 'Bigfoot', AVATAR_TYPE_TRANSCENDANT, 'Bigfoot', 'Cryptid',),
            ('T2', 'Mothman', AVATAR_TYPE_TRANSCENDANT, 'Mothman', 'Cryptid',),
            ('T3', 'Frogman', AVATAR_TYPE_TRANSCENDANT, 'Frogman', 'Cryptid',),
            ('T4', 'SkunkApe', AVATAR_TYPE_TRANSCENDANT, 'SkunkApe', 'Cryptid',),

            # Fallback Avatars
            ('F1', 'Fallback-1', AVATAR_TYPE_FALLBACK, 'DefaultM', '',),
            ('F2', 'Fallback-2', AVATAR_TYPE_FALLBACK, 'DefaultF', '',),
        ]

        for index, avatar in enumerate(avatar_data):
            avatar = (index + 1,) + avatar
            if len(avatar) == 6:
                avatar = avatar + (False,)

            self.queryHandler.execute_query(TGOMMO_INSERT_NEW_USER_AVATAR, params=avatar)

            # for avatars unlocked server wide, insert a starter record into avatar link table
            if avatar[3] == AVATAR_TYPE_DEFAULT or avatar[3] == AVATAR_TYPE_SECRET:
                avatar_id = avatar[1]
                user_id = -1 if avatar[3] == AVATAR_TYPE_DEFAULT else 1
                self.queryHandler.execute_query(TGOMMO_INSERT_NEW_USER_AVATAR_LINK, params=(avatar_id, user_id))
    def insert_user_avatar_unlock_condition_records(self):
        avatar_data = [
            # COLLECTION QUESTS
            ('Donkey Kong', ('Q1', AVATAR_DONKEY_KONG_QUEST_QUERY, 20)),
            ('Big Bird', ('Q2', AVATAR_BIG_BIRD_QUEST_QUERY, 18)),
            ('Gex', ('Q3', AVATAR_GEX_QUEST_QUERY, 3)),
            ('Kermit', ('Q4', AVATAR_KERMIT_QUEST_QUERY, 2)),
            ('Hornet', ('Q5', AVATAR_HORNET_QUEST_QUERY, 5)),
            ('TMNT', ('Q6', AVATAR_VARIANTS_QUEST_1_QUERY, 10)),
            ('HGSS', ('Q7', AVATAR_MYTHICAL_QUEST_QUERY, 1)),
            ('Homer', ('Q8', AVATAR_MYTHICAL_QUEST_QUERY, 5)),
            # WAVE 2
            ('Mordecai', ('Q10', AVATAR_MORDECAI_QUEST_QUERY, AVATAR_QUEST_UNCOMMON_COUNT)),
            ('Rigby', ('Q11', AVATAR_RIGBY_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
            ('Squirrel Girl', ('Q12', AVATAR_SQUIRRELGIRL_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
            ('Noko Shikanoko', ('Q13', AVATAR_NOKOSHIKANOKO_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
            ('Huntrix', ('Q14', AVATAR_LEGENDARY_QUEST_QUERY, 3)),
            ('Shuma Gorath', ('Q15', AVATAR_TOTAL_EPIC_QUEST_QUERY, 10)),
            ('Gary', ('Q16', AVATAR_GARY_QUEST_QUERY, AVATAR_QUEST_UNCOMMON_COUNT)),
            #WAVE 3
            ('Bugs', ('Q17', AVATAR_BUGS_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
            ('Daffy', ('Q18', AVATAR_DAFFY_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
            ('Puss in Boots', ('Q19', AVATAR_PUSSINBOOTS_QUEST_QUERY, AVATAR_QUEST_COMMON_COUNT)),
            ('Bubsy', ('Q20', AVATAR_BUBSY_QUEST_QUERY, AVATAR_QUEST_RARE_COUNT)),
            ('Spider-Man', ('Q21', AVATAR_SPIDERMAN_QUEST_QUERY, AVATAR_QUEST_UNCOMMON_COUNT)),
            ('Cynthia', ('Q22', AVATAR_CYNTHIA_QUEST_QUERY, 100)),
            # WAVE 3.5
            ('Marceline', ('Q23', AVATAR_MARCELINE_QUEST_QUERY, 20)),

            # Transcendant Avatars
            ('Bigfoot', ('T1', AVATAR_BIGFOOT_QUEST_QUERY,1, True)),
            ('Mothman', ('T2', AVATAR_MOTHMAN_QUEST_QUERY,1, True)),
            ('Frogman', ('T3', AVATAR_FROGMAN_QUEST_QUERY,1, True)),
            ('SkunkApe', ('T4', AVATAR_SKUNK_APE_QUEST_QUERY,1, True)),
        ]

        for index, avatar in enumerate(avatar_data):
            avatar_params = avatar[1]
            if len(avatar_params) == 3:
                avatar_params = avatar_params + (False,)

            self.queryHandler.execute_query(TGOMMO_INSERT_NEW_AVATAR_UNLOCK_CONDITION, params=avatar_params)

    def insert_item_records(self):
        item_data = [
            # Creature Inventory Storage
            (ITEM_ID_CREATURE_INVENTORY_STORAGE_EXPANSION, 'Creature Storage Upgrade', ITEM_TYPE_GAMEPLAY_MECHANICS, 'Increases your creature storage capacity by 100.', TGOMMO_RARITY_NORMAL, False, '', 1),

            # Name Tags
            (f'{ITEM_TYPE_NAMETAG}_1', 'NameTag', ITEM_TYPE_NAMETAG, 'Lets you rename any creature you already caught', TGOMMO_RARITY_COMMON, False, '', 1),

            # Baits
            (ITEM_ID_BAIT, 'Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch.', TGOMMO_RARITY_NORMAL, True, '', 1),
            (ITEM_ID_COMMON_BAIT, 'Common Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be common.', TGOMMO_RARITY_COMMON, True, '', 1),
            (ITEM_ID_UNCOMMON_BAIT, 'Uncommon Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be uncommon.', TGOMMO_RARITY_UNCOMMON, True, '', 1),
            (ITEM_ID_RARE_BAIT, 'Rare Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be rare.', TGOMMO_RARITY_RARE, True, '', 1),
            (ITEM_ID_EPIC_BAIT, 'Epic Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be epic.', TGOMMO_RARITY_EPIC, True, '', 1),
            (ITEM_ID_LEGENDARY_BAIT, 'Legendary Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be legendary.', TGOMMO_RARITY_LEGENDARY, True, '', 1),
            (ITEM_ID_MYTHICAL_BAIT, 'Mythical Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be mythical.', TGOMMO_RARITY_MYTHICAL, True, '', 1),
            (ITEM_ID_TRANSCENDANT_BAIT, 'Transcendant Bait', ITEM_TYPE_BAIT, 'Allows you to summon a random creature only you can catch. The creature will always be transcendant.', TGOMMO_RARITY_TRANSCENDANT, False, '', 1),
            (ITEM_ID_OMNIPOTENT_BAIT, 'Omnipotent Bait', ITEM_TYPE_BAIT, 'Allows you to summon any discovered creature of your choice. Only you can catch this creature.', TGOMMO_RARITY_OMNIPOTENT, False, '', 1),

            # Megaphones
            (ITEM_TYPE_MEGAPHONE, 'Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a new creature spawns.', TGOMMO_RARITY_NORMAL, False, '', -1),
            (ITEM_ID_COMMON_MEGAPHONE, 'Common Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a common creature spawns.', TGOMMO_RARITY_COMMON, False, '', -1),
            (ITEM_ID_UNCOMMON_MEGAPHONE, 'Uncommon Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a uncommon creature spawns.', TGOMMO_RARITY_UNCOMMON, False, '', -1),
            (ITEM_ID_RARE_MEGAPHONE, 'Rare Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a rare creature spawns.', TGOMMO_RARITY_RARE, False, '', -1),
            (ITEM_ID_EPIC_MEGAPHONE, 'Epic Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever an epic creature spawns.', TGOMMO_RARITY_EPIC, False, '', -1),
            (ITEM_ID_LEGENDARY_MEGAPHONE, 'Legendary Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a legendary creature spawns.', TGOMMO_RARITY_LEGENDARY, False, '', -1),
            (ITEM_ID_MYTHICAL_MEGAPHONE, 'Mythical Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a mythical creature spawns.', TGOMMO_RARITY_MYTHICAL, False, '', -1),
            (ITEM_ID_TRANSCENDANT_MEGAPHONE, 'Transcendant Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you whenever a transcendant creature spawns. Breaks after a single catch, though', TGOMMO_RARITY_TRANSCENDANT, False, '', 1),
            (ITEM_ID_OMNIPOTENT_MEGAPHONE, 'Omnipotent Megaphone', ITEM_TYPE_MEGAPHONE, 'Will notify you when any creature of your choice spawns. Breaks after a single catch, though.', TGOMMO_RARITY_OMNIPOTENT, False, '', 1),

            # Charms
            (ITEM_ID_CHARM, 'Charm', ITEM_TYPE_CHARM, 'Increases the amount of creatures that will spawn for the next 30 minutes.', TGOMMO_RARITY_NORMAL, True, '', 1),
            (ITEM_ID_COMMON_CHARM, 'Common Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for common creatures. Lasts for 30 minutes', TGOMMO_RARITY_COMMON, True, '', 1),
            (ITEM_ID_UNCOMMON_CHARM, 'Uncommon Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for uncommon creatures. Lasts for 30 minutes', TGOMMO_RARITY_UNCOMMON, True, '', 1),
            (ITEM_ID_RARE_CHARM, 'Rare Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for rare creatures. Lasts for 30 minutes', TGOMMO_RARITY_RARE, True, '', 1),
            (ITEM_ID_EPIC_CHARM, 'Epic Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for epic creatures. Lasts for 30 minutes', TGOMMO_RARITY_EPIC, True, '', 1),
            (ITEM_ID_LEGENDARY_CHARM, 'Legendary Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for legendary creatures. Lasts for 30 minutes', TGOMMO_RARITY_LEGENDARY, True, '', 1),
            (ITEM_ID_MYTHICAL_CHARM, 'Mythical Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for mythical creatures. Lasts for 30 minutes', TGOMMO_RARITY_MYTHICAL, True, '', 1),
            (ITEM_ID_TRANSCENDANT_CHARM, 'Transcendant Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for transcendant creatures. Lasts for 30 minutes', TGOMMO_RARITY_TRANSCENDANT, False, '', 1),
            (ITEM_ID_OMNIPOTENT_CHARM, 'Omnipotent Charm', ITEM_TYPE_CHARM, 'Increases the spawn chances for any creature of your choice. Lasts for 10 minutes', TGOMMO_RARITY_OMNIPOTENT, False, '', 1),
        ]

        for index, item in enumerate(item_data):
            item = (index + 1,) + item
            self.queryHandler.execute_query(TGOMMO_INSERT_NEW_INVENTORY_ITEM, params=item)


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