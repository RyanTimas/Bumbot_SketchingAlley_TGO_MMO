'''GENERAL_CONSTANTS'''
import datetime
import pytz


# todo: move to file paths
'''EMBED ICONS'''
TGOMMO_CREATURE_EMBED_LOCATION_ICON = "https://cdn-icons-png.flaticon.com/512/535/535137.png"
TGOMMO_CREATURE_EMBED_CLOCK_ICON = "https://cdn-icons-png.flaticon.com/512/4305/4305432.png"

'''PLAYER PROFILE SCREEN'''
PLAYER_PROFILE_AVATAR_PREFIX = "Avatar_"
PLAYER_PROFILE_BACKGROUND_PREFIX = "Background_"

# todo: move some of this logic to a game_state.json type format?
""" ----- UNIVERSAL FEATURES  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region TIME OF DAY
BASE_TIMEZONE = pytz.timezone('US/Eastern')

DAY = "Day"
NIGHT = "Night"
DUSK = "dusk"
DAWN = "dawn"
BOTH = "both"
# endregion
# region RGB COLOR VALUES
FONT_COLOR_BLACK = (0, 0, 0)
FONT_COLOR_WHITE = (255, 255, 255)
FONT_COLOR_GOLD = (241, 196, 15)
FONT_COLOR_DARK_GRAY = (88, 88, 87)
TRANSPARENT_IMG_BG = (0, 0, 0, 0)
# endregion

""" ----- AVATARS  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region Avatar Types
AVATAR_TYPE_DEFAULT = "Default"
AVATAR_TYPE_SECRET = "Secret"

AVATAR_TYPE_QUEST = "Quest"
AVATAR_TYPE_SHOP = "Shop"
AVATAR_TYPE_EVENT = "Event"
AVATAR_TYPE_TRANSCENDANT = "Transcendant"

AVATAR_TYPE_CUSTOM = "Custom"
AVATAR_TYPE_FALLBACK = "Fallback"

AVATAR_TYPE_SORT_ORDER = {
    AVATAR_TYPE_DEFAULT: 1,
    AVATAR_TYPE_SECRET: 2,
    AVATAR_TYPE_EVENT: 3,
    AVATAR_TYPE_QUEST: 4,
    AVATAR_TYPE_TRANSCENDANT: 5,
    AVATAR_TYPE_FALLBACK: 6,
    AVATAR_TYPE_CUSTOM: 7
}

# endregion

""" ----- CREATURES  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region Creature Kingdoms
MAMMAL = "Mammal"
BIRD = "Bird"
REPTILE = "Reptile"
AMPHIBIAN = "Amphibian"
INSECT = "Insect"
BUG = "Bug"
FISH = "Fish"

MOLLUSK = "Mollusk"
CRUSTACEAN = "Crustacean"
ARACHNID = "Arachnid"
CLITELLATA = "Clitellata"
MYRIAPOD = "Myriapod"
ARTHROPOD = "Arthropod"

MYSTICAL = "Mystical"
# endregion
# region Rarities
TGOMMO_RARITY_COMMON = "Common"
TGOMMO_RARITY_UNCOMMON = "Uncommon"
TGOMMO_RARITY_RARE = "Rare"
TGOMMO_RARITY_EPIC = "Epic"
TGOMMO_RARITY_LEGENDARY = "Legendary"
TGOMMO_RARITY_MYTHICAL = "Mythical"
TGOMMO_RARITY_TRANSCENDANT = "Transcendant"

TGOMMO_RARITY_NORMAL = "Normal"
TGOMMO_RARITY_EXOTIC = "Exotic"
TGOMMO_RARITY_EVENT = "Event"
TGOMMO_RARITY_OMNIPOTENT = "Omnipotent"
# endregion

""" ----- ENVIRONMENTS  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region Dex Numbers
EASTERN_US_DEX_NO = 1
FLORIDA_DEX_NO = 2
# endregion
# region Sub Environments
SUB_ENVIRONMENT_FOREST = "forest"
SUB_ENVIRONMENT_FIELD = "field"
SUB_ENVIRONMENT_POND = "pond"
SUB_ENVIRONMENT_GARDEN = "garden"
SUB_ENVIRONMENT_RIVER = "river"
SUB_ENVIRONMENT_BEACH = "beach"
SUB_ENVIRONMENT_SWAMP = "swamp"
SUB_ENVIRONMENT_CITY = "city"
SUB_ENVIRONMENT_PIER = "pier"
SUB_ENVIRONMENT_OCEAN = "ocean"
SUB_ENVIRONMENT_MOUNTAIN = "mountain"
# endregion

""" ----- ITEMS  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region Item Types
ITEM_TYPE_GAMEPLAY_MECHANICS = 'Gameplay Mechanics'
ITEM_TYPE_NAMETAG = 'NameTag'
ITEM_TYPE_BAIT = 'Bait'
ITEM_TYPE_MEGAPHONE = 'Megaphone'
ITEM_TYPE_CHARM = 'Charm'

ITEM_INVENTORY_EXCLUDED_ITEM_TYPES = [ITEM_TYPE_GAMEPLAY_MECHANICS, ITEM_TYPE_MEGAPHONE]
# endregion

""" ----- GAMEPLAY MECHANICS  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
""" ----- CREATURE CATCH  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region Creature Catch Rates
DEFAULT_CREATURE_SPAWN_RATE_LOW_END = 3
DEFAULT_CREATURE_SPAWN_RATE_HIGH_END = 5
SPAWN_BOOST_ON = False

DEFAULT_MYTHICAL_SPAWN_CHANCE = 275
DEFAULT_MYTHICAL_SPAWN_COIN_FLIPS = 8
# endregion
# region XP Values
CREATURE_DIVIDER_LINE = "__ \t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t __"
CREATURE_SUCCESSFUL_CATCH_LINE = "Successful Catch                                               "
CREATURE_FIRST_CATCH_LINE = "First Time Catch                                              *+250 xp*"
CREATURE_FIRST_CATCH_VARIANT_LINE = "First Time Catch For Variant                        *+175 xp*"
CREATURE_FIRST_SERVER_CATCH_LINE = "New Species For Server                             *+1000 xp*"
MYTHICAL_CATCH_LINE = "Mythical Creature                                         *+1000 xp*"
CREATURE_TOTAL_XP_LINE = "✨ **Total 150000 xp** ✨"
# todo: user caught new form of this species +2500 xp
# todo: user caught 10 of this species +5000 xp
# todo: user caught 100 of this species +25000 xp
# todo: user caught 10th instance of this species on server +5000 xp
# todo: user caught 100th instance of this species on server +25000 xp
# todo: user caught every species in a location +100000 xp
# todo: when every species in a location is caught, everyone who caught a species in that location gets +5000 xp
CREATURE_TOTAL_XP_LINE_CENTERED = "‎                         ✨ **Total 150000 xp** ✨                        ‎ "
# endregion

# region Event Variables
NEXT_EVENT_START_TIMESTAMP = datetime.datetime(2025, 10, 31, 0, 0, 0)
NEXT_EVENT_END_TIMESTAMP = datetime.datetime(2025, 10, 31, 23, 59, 59)
IS_EVENT = NEXT_EVENT_START_TIMESTAMP <= datetime.datetime.now() <= NEXT_EVENT_END_TIMESTAMP

EVENT_NAME = "Halloween"
EVENT_SPAWN_POOL = [(18,5)]
EVENT_MYTHICAL_SPAWN_CHANCE = 32
EVENT_MYTHICAL_SPAWN_COIN_FLIPS = 6
# endregion
# region User Catch Trackers
USER_CATCHES_DAILY = {}
USER_CATCHES_HOURLY = {}
# endregion
MYTHICAL_SPAWN_CHANCE = EVENT_MYTHICAL_SPAWN_CHANCE if IS_EVENT else DEFAULT_MYTHICAL_SPAWN_CHANCE
MYTHICAL_SPAWN_COIN_FLIPS = EVENT_MYTHICAL_SPAWN_COIN_FLIPS if IS_EVENT else DEFAULT_MYTHICAL_SPAWN_COIN_FLIPS

# region Encounter Image Dimension Constants
CREATURE_ENCOUNTER_TEXT_BOX_WIDTH = 426

CREATURE_ENCOUNTER_FOREGROUND_IMAGE_RESIZE_PERCENT = 0.9
CREATURE_ENCOUNTER_FOREGROUND_IMAGE_X_OFFSET = 0
CREATURE_ENCOUNTER_FOREGROUND_IMAGE_Y_OFFSET = -24
CREATURE_ENCOUNTER_NAME_TEXT_SIZE = 48
# endregion

""" ----- ENCYCLOPEDIA  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region Encyclopedia Display Keys
ENCYCLOPEDIA_VARIANTS_DISPLAY_KEY = "variants"
ENCYCLOPEDIA_MYTHICAL_DISPLAY_KEY = "mythical"
ENCYCLOPEDIA_DAY_SPAWNS_DISPLAY_KEY = "day_spawns"
ENCYCLOPEDIA_NIGHT_SPAWNS_DISPLAY_KEY = "night_spawns"
ENCYCLOPEDIA_NO_EXPANDED_DISPLAY_KEY = "no_expanded_display"
ENCYCLOPEDIA_BASE_EXPANDED_DISPLAY_KEY = "base_expanded_display"
ENCYCLOPEDIA_EXPANDED_TIME_DISPLAY_KEY = "expanded_time_display"
ENCYCLOPEDIA_EXPANDED_RARITY_DISPLAY_KEY = "expanded_rarity_display"
ENCYCLOPEDIA_EXPANDED_CLASS_DISPLAY_KEY = "expanded_class_display"
# endregion
# region Encylopedia Modes
ENCYCLOPEDIA_VERBOSE_MODE = "verbose"
ENCYCLOPEDIA_XL_MODE = "XL"
# endregion

""" ----- PLAYER PROFILE  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region Player Profile Creature Variables
PLAYER_PROFILE_CREATURE_RESIZE_PERCENT = 0.5
PLAYER_PROFILE_CREATURE_COORDINATES = [
    (183, 444), (1097, 444),    # middle row
    (426, 260), (852, 260),     # back row
    (426, 580), (852, 580)      # front row
]
# endregion
# region Player Profile Tab Keys
PLAYER_PROFILE_TAB_OPEN_TEAM = "Team"
PLAYER_PROFILE_TAB_OPEN_COLLECTIONS = "Collections"
PLAYER_PROFILE_TAB_CLOSED = "Closed"
# endregion

""" ----- AVATAR BOARD  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region Avatar Board Tabs
AVATAR_INVENTORY_QUEST_TAB_KEY = "AVATAR_QUESTS"
AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY = "UNLOCKED_AVATARS"
# endregion

""" ----- CREATURE INVENTORY  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region Creature Inventory Expansion Variables
BASE_CREATURE_STORAGE_EXPANSIONS = 8
MAX_CREATURE_STORAGE_EXPANSIONS = 15
CREATURE_STORAGE_EXPANSION_BASE_COST = 250
# endregion

# region Creature Inventory Workflow States
CREATURE_INVENTORY_VIEW_WORKFLOW_STATE_INITIAL = "initial"
CREATURE_INVENTORY_VIEW_WORKFLOW_STATE_INTERACTION = "interaction"
CREATURE_INVENTORY_VIEW_WORKFLOW_STATE_CONFIRMATION = "confirmation"
CREATURE_INVENTORY_VIEW_WORKFLOW_STATE_FINALIZED = "finalized"
# endregion

# region Creature Expansion Keys
CREATURE_INVENTORY_FILTER_EXPANSION_KEY = "filter_expansion"
CREATURE_INVENTORY_ORDER_EXPANSION_KEY = "order_expansion"
CREATURE_INVENTORY_CREATURE_MANAGEMENT_EXPANSION_KEY = "creature_management"
# endregion
# region Creature Inventory Filter Keys
CREATURE_INVENTORY_FILTER_MYTHIC = "mythic_only"
CREATURE_FAVORITE_FILTER_MYTHIC = "favorite_only"
CREATURE_NICKNAME_FILTER_MYTHIC = "nickname_only"
# endregion
# region Creature Inventory Sort Keys
CREATURE_NICKNAME_SORT_ALPHABETICAL = 'alphabetical'
CREATURE_NICKNAME_SORT_DEX_NO = 'dex_no'
CREATURE_NICKNAME_SORT_CAUGHT_DATE = 'caught_date'
# endregion
# region Creature Inventory Mode Keys
CREATURE_INVENTORY_MODE_RELEASE = "Release"
CREATURE_INVENTORY_MODE_FAVORITE = "Favorite"
CREATURE_INVENTORY_MODE_DEFAULT = "Default"
CREATURE_INVENTORY_MODE_RELEASE_RESULTS = "Release Results"
# endregion

""" ----- ITEM INVENTORY  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""


""" ----- COLLECTIONS  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region Collection Keywords
VARIANTS_COLLECTION_KEYWORD = "Variants"
# endregion


""" ----- QUESTS  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region generic Quest Totals
AVATAR_QUEST_COMMON_COUNT = 100
AVATAR_QUEST_UNCOMMON_COUNT = 50
AVATAR_QUEST_RARE_COUNT = 25
AVATAR_QUEST_EPIC_COUNT = 12
AVATAR_QUEST_LEGENDARY_COUNT = 5
# endregion


""" ----- SPECIFIC IDS  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
""" ----- ITEM IDS  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region ITEM IDS
ITEM_ID_CREATURE_INVENTORY_STORAGE_EXPANSION = 'Creature_Inventory_Storage_Expansion'

ITEM_ID_NAMETAG  = f"{ITEM_TYPE_NAMETAG}_0"

ITEM_ID_BAIT  = f"{ITEM_TYPE_BAIT}_0"
ITEM_ID_COMMON_BAIT  = f"{ITEM_TYPE_BAIT}_1"
ITEM_ID_UNCOMMON_BAIT  = f"{ITEM_TYPE_BAIT}_2"
ITEM_ID_RARE_BAIT  = f"{ITEM_TYPE_BAIT}_3"
ITEM_ID_EPIC_BAIT  = f"{ITEM_TYPE_BAIT}_4"
ITEM_ID_LEGENDARY_BAIT  = f"{ITEM_TYPE_BAIT}_5"
ITEM_ID_MYTHICAL_BAIT  = f"{ITEM_TYPE_BAIT}_6"
ITEM_ID_TRANSCENDANT_BAIT  = f"{ITEM_TYPE_BAIT}_7"
ITEM_ID_OMNIPOTENT_BAIT  = f"{ITEM_TYPE_BAIT}_8"

ITEM_ID_CHARM = f"{ITEM_TYPE_CHARM}_0"
ITEM_ID_COMMON_CHARM = f"{ITEM_TYPE_CHARM}_1"
ITEM_ID_UNCOMMON_CHARM = f"{ITEM_TYPE_CHARM}_2"
ITEM_ID_RARE_CHARM = f"{ITEM_TYPE_CHARM}_3"
ITEM_ID_EPIC_CHARM = f"{ITEM_TYPE_CHARM}_4"
ITEM_ID_LEGENDARY_CHARM = f"{ITEM_TYPE_CHARM}_5"
ITEM_ID_MYTHICAL_CHARM = f"{ITEM_TYPE_CHARM}_6"
ITEM_ID_TRANSCENDANT_CHARM = f"{ITEM_TYPE_CHARM}_7"
ITEM_ID_OMNIPOTENT_CHARM = f"{ITEM_TYPE_CHARM}_8"

ITEM_ID_MEGAPHONE = f"{ITEM_TYPE_MEGAPHONE}_0"
ITEM_ID_COMMON_MEGAPHONE = f"{ITEM_TYPE_MEGAPHONE}_1"
ITEM_ID_UNCOMMON_MEGAPHONE = f"{ITEM_TYPE_MEGAPHONE}_2"
ITEM_ID_RARE_MEGAPHONE = f"{ITEM_TYPE_MEGAPHONE}_3"
ITEM_ID_EPIC_MEGAPHONE = f"{ITEM_TYPE_MEGAPHONE}_4"
ITEM_ID_LEGENDARY_MEGAPHONE = f"{ITEM_TYPE_MEGAPHONE}_5"
ITEM_ID_MYTHICAL_MEGAPHONE = f"{ITEM_TYPE_MEGAPHONE}_6"
ITEM_ID_TRANSCENDANT_MEGAPHONE = f"{ITEM_TYPE_MEGAPHONE}_7"
ITEM_ID_OMNIPOTENT_MEGAPHONE = f"{ITEM_TYPE_MEGAPHONE}_8"
# endregion



