'''GENERAL_CONSTANTS'''
IS_EVENT = False
EVENT_IDS = []
MYTHICAL_SPAWN_CHANCE = 300  # 1 in 300 chance of a mythical spawning

# track user timeouts
USER_CATCHES_DAILY = {}
USER_CATCHES_HOURLY = {}
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''VIEW WORKFLOW STATES'''
VIEW_WORKFLOW_STATE_INTERACTION = "interaction"
VIEW_WORKFLOW_STATE_CONFIRMATION = "confirmation"
VIEW_WORKFLOW_STATE_FINALIZED = "finalized"



'''TIME OF DAY'''
DAY = "Day"
NIGHT = "Night"
DUSK = "dusk"
DAWN = "dawn"
BOTH = "both"

"""COLLECTIONS KEYWORDS"""
VARIANTS = "Variants"
MYTHICAL_TEXT = "Mythical"

'''EMBED ICONS'''
TGOMMO_CREATURE_EMBED_LOCATION_ICON = "https://cdn-icons-png.flaticon.com/512/535/535137.png"
TGOMMO_CREATURE_EMBED_CLOCK_ICON = "https://cdn-icons-png.flaticon.com/512/4305/4305432.png"


'''CREATURE CATCH XP LINES'''
CREATURE_DIVIDER_LINE = "__ \t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t __"
CREATURE_SUCCESSFUL_CATCH_LINE = "Successful Catch                                               "
CREATURE_FIRST_CATCH_LINE = "First Time Catch                                              *+2500 xp*"
CREATURE_FIRST_SERVER_CATCH_LINE = "New Species For Server                             *+10000 xp*"
MYTHICAL_CATCH_LINE = "Mythical Creature                                         *+10000 xp*"
CREATURE_TOTAL_XP_LINE = "✨ **Total 150000 xp** ✨"
# todo: user caught new form of this species +2500 xp
# todo: user caught 10 of this species +5000 xp
# todo: user caught 100 of this species +25000 xp
# todo: user caught 10th instance of this species on server +5000 xp
# todo: user caught 100th instance of this species on server +25000 xp
# todo: user caught every species in a location +100000 xp
# todo: when every species in a location is caught, everyone who caught a species in that location gets +5000 xp
CREATURE_TOTAL_XP_LINE_CENTERED = "‎                         ✨ **Total 150000 xp** ✨                        ‎ "


'''AVATAR QUESTS'''
AVATAR_QUEST_COMMON_COUNT = 100
AVATAR_QUEST_UNCOMMON_COUNT = 50
AVATAR_QUEST_RARE_COUNT = 25
AVATAR_QUEST_EPIC_COUNT = 12
AVATAR_QUEST_LEGENDARY_COUNT = 5

'''ENCOUNTER SCREEN'''
TEXT_BOX_WIDTH = 426

ENCOUNTER_SCREEN_FOREGROUND_IMAGE_RESIZE_PERCENT = 0.9
ENCOUNTER_SCREEN_FOREGROUND_IMAGE_X_OFFSET = 0
ENCOUNTER_SCREEN_FOREGROUND_IMAGE_Y_OFFSET = -24

FONT_COLOR_BLACK = (0, 0, 0)
FONT_COLOR_WHITE = (255, 255, 255)
FONT_COLOR_GOLD = (241, 196, 15)
FONT_COLOR_DARK_GRAY = (88, 88, 87)
TRANSPARENT_IMG_BG = (0, 0, 0, 0)

CREATURE_NAME_TEXT_SIZE = 48
SUPPORTING_TEXT_SIZE = 12


'''PLAYER PROFILE SCREEN'''
PLAYER_PROFILE_AVATAR_PREFIX = "Avatar_"
PLAYER_PROFILE_BACKGROUND_PREFIX = "Background_"

PLAYER_PROFILE_CREATURE_RESIZE_PERCENT = 0.5
PLAYER_PROFILE_CREATURE_COORDINATES = [
    (183, 444), (1097, 444),    # middle row
    (426, 260), (852, 260),     # back row
    (426, 580), (852, 580)      # front row
]

'''CREATURE BOXES'''
ALPHABETICAL_ORDER = 'alphabetical'
DEX_NO_ORDER = 'dex_no'
CAUGHT_DATE_ORDER = 'caught_date'

CREATURE_INVENTORY_RELEASE_MODE = "Release"
CREATURE_INVENTORY_FAVORITE_MODE = "Favorite"

'''CREATURE KINGDOM NAMES'''
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
MYSTICAL = "Mystical"

'''CREATURE RARITY NAMES'''
TGOMMO_RARITY_COMMON = "Common"
TGOMMO_RARITY_UNCOMMON = "Uncommon"
TGOMMO_RARITY_RARE = "Rare"
TGOMMO_RARITY_EPIC = "Epic"
TGOMMO_RARITY_LEGENDARY = "Legendary"
TGOMMO_RARITY_MYTHICAL = "Mythical"
TGOMMO_RARITY_EXOTIC = "Exotic"
TGOMMO_RARITY_TRANSCENDANT = "Transcendant"
TGOMMO_RARITY_EVENT = "Event"

'''------------------'''
'''ENVIRONMENTS'''
'''------------------'''
'''ENVIRONMENT DEX NUMBERS'''
EASTERN_US_FOREST_NO = 1
EVERGLADES_NO = 2

'''SUB ENVIRONMENT TYPES'''
SUB_ENVIRONMENT_FOREST = "forest"
SUB_ENVIRONMENT_FIELD = "field"
SUB_ENVIRONMENT_POND = "pond"
SUB_ENVIRONMENT_GARDEN = "garden"
SUB_ENVIRONMENT_RIVER = "river"
SUB_ENVIRONMENT_BEACH = "beach"

'''----------'''
'''AVATARS'''
'''----------'''
AVATAR_TYPE_DEFAULT = "Default"
AVATAR_TYPE_SECRET = "Secret"

AVATAR_TYPE_QUEST = "Quest"
AVATAR_TYPE_SHOP = "Shop"
AVATAR_TYPE_EVENT = "Event"
AVATAR_TYPE_TRANSCENDANT = "Transcendant"

AVATAR_TYPE_CUSTOM = "Custom"
AVATAR_TYPE_FALLBACK = "Fallback"


'''HELP MENU STRINGS'''
TGOMMO_HELP_MENU_TITLE = (
    "# :small_red_triangle:TGO MMO Help Menu:small_red_triangle_down:"
    "\n## :herb: Welcome to **__TGO MMO__** the first-ever Sketching Alley Game! :herb:"
    "\n:point_right: This message will act as a handy how-to guide for interacting with the game. Below you will Find Explanations of what the buttons do and commands you can enter in chat. Please note that only you can interact with a menu you open. Others will not be able to mess with your navigation & vice versa."
)

TGOMMO_HELP_MENU_BUTTON_DESCRIPTION = (
    "\n\n## BUTTONS"
    "\nButtons allow you to navigate the TGO MMO UI from one easy to use place. More buttons to come in the future :wink:\n"
)
TGOMMO_HELP_MENU_BUTTON_OPTIONS = (
    "\n```ansi"
    "\n[2;34mUser Encyclopedia:[0m View your personal encyclopedia of caught creatures."
    "\n[2;31m[2;32mServer Encyclopedia:[0m[2;31m[0m View the encyclopedia of all creatures caught by the server as a collective."
    "\n"
    "\n[2;31mClose:[0m Close this menu."
    "```"
)

TGOMMO_HELP_MENU_COMMANDS_DESCRIPTION_1 = (
    "\n## COMMANDS"
    "\nCommands are used to interact with the TGOMMO system in a more advanced way. While the TGO MMO Menu provides all of the basic gameplay necessities, commands offer expanded features and allow for a more personalized experience. They can only be used in the TGO MMO channel."
)
TGOMMO_HELP_MENU_COMMANDS_OPTIONS_1 = (
    "\n```ansi"
    "\n* Commands are called using an '[2;32m![0m'[2;37m [0mfollowed by a [2;35m[2;35mkeyword[0m[2;35m[0m[2;37m. [0m "
    "\n* You can add additional [2;37m[2;36m[2;36mparameters[0m[2;36m[0m[2;37m[0m to commands to customize their behavior."
    "\n* Commands are formatted as: \"[2;35m[2;33m[2;32m![0m[2;33m[0m[2;35m[2;35mcommand[0m[2;35m[0m [2;35m[2;35m[2;36m[2;36mparameter1[0m[2;36m[0m[2;35m[0m[2;35m[0m [2;36m[2;36mparameter2[0m[2;36m[0m[2;37m\"[0m"
    "```"
)
TGOMMO_HELP_MENU_COMMANDS_DESCRIPTION_2 = (
    "\n### The following commands are available:"
)
TGOMMO_HELP_MENU_COMMANDS_OPTIONS_2 = (
    "\n```ansi"
    "\n[2;37m[2;35mtgommo-help[0m[2;37m: [0mBrings up the Main Menu for TGOMMO."
    "\n[2;35mcaught_creatures[0m: Displays encyclopedia view for caught creatures."
    "\n[2;37m [0m* [2;36m[2;36mserver[0m[2;36m[0m: Displays encyclopedia for the server"
    "\n * [2;36m[2;36m{user_id}[0m[2;36m[0m: Displays the encyclopedia for a specific user, inserts their"
    "\n              userId, do NOT tag them or use their username"
    "\n[2;36m[2;37m * [0m[2;36m[2;36mvariants[0m[2;36m[0m: Opens encyclopedia in variant mode."
    "\n[2;36m[2;37m * [0m[2;36m[2;36mmythical[0m[2;36m[0m: Opens encyclopedia in mythical mode"
    "```"
)

TGOMMO_HELP_MENU_FOOTER = "-# If you have any questions or feature requests, please reach out to Bumbiss for help! :bumbiss_thumbs_up:"

