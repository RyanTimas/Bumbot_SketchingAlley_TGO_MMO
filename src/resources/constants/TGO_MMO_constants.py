'''GENERAL_CONSTANTS'''
IS_EVENT = False
EVENT_IDS = []
MYTHICAL_SPAWN_CHANCE = 250  # 1 in 250 chance of a mythical spawning

DAY = "Day"
NIGHT = "Night"
DUSK = "dusk"
DAWN = "dawn"
BOTH = "both"


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
PLAYER_PROFILE_CREATURE_RESIZE_PERCENT = 0.5
PLAYER_PROFILE_CREATURE_COORDINATES = [
    (183, 444), (1097, 444),    # middle row
    (426, 260), (852, 260),     # back row
    (426, 580), (852, 580)      # front row
]

'''CREATURE IMAGES'''
N00_BASE_CREATURE_IMAGE_FILE = "BASE_CREATURE.png"
N00_BASE_CREATURE_IMAGE_FILE_ENCOUNTER = "BASE_CREATURE_E.png"
N00_BASE_CREATURE_IMAGE_FILE_FLEE = "BASE_CREATURE_F.png"
N00_BASE_CREATURE_IMAGE_FILE_CATCH = "BASE_CREATURE_C.png"
N00_BASE_CREATURE_IMAGE_FILE_THUMBNAIL = "BASE_CREATURE_THUMB.png"

DEER_IMAGE_ROOT = "Deer"
SQUIRREL_IMAGE_ROOT = "Squirrel"
RABBIT_IMAGE_ROOT = "Rabbit"
CHIPMUNK_IMAGE_ROOT = "Chipmunk"
RACOON_IMAGE_ROOT = "Raccoon"
ROBIN_IMAGE_ROOT = "Robin"
SPARROW_IMAGE_ROOT = "HouseSparrow"
BLUEJAY_IMAGE_ROOT = "BlueJay"
GOLDFINCH_IMAGE_ROOT = "Goldfinch"
CARDINAL_IMAGE_ROOT = "Cardinal"
MONARCH_IMAGE_ROOT = "Monarch"
MANTIS_IMAGE_ROOT = "Mantis"
GARTERSNAKE_IMAGE_ROOT = "Snake"
TURTLE_IMAGE_ROOT = "BoxTurtle"
TOAD_IMAGE_ROOT = "Toad"
MALLARD_IMAGE_ROOT = "Mallard"
TURKEY_IMAGE_ROOT = "Turkey"
EAGLE_IMAGE_ROOT = "Eagle"
GREAT_HORNED_OWL_IMAGE_ROOT = "GreatHornedOwl"
OPOSSUM_IMAGE_ROOT = "Opossum"
REDFOX_IMAGE_ROOT = "RedFox"
BOBCAT_IMAGE_ROOT = "Bobcat"
BLACKBEAR_IMAGE_ROOT = "BlackBear"
MOOSE_IMAGE_ROOT = "Moose"
WOLF_IMAGE_ROOT = "Wolf"

CAT_IMAGE_ROOT = "Cat"
MOUSE_IMAGE_ROOT = "Mouse"
GROUNDHOG_IMAGE_ROOT = "Groundhog"
MOURNING_DOVE_IMAGE_ROOT = "MourningDove"
CANADA_GOOSE_IMAGE_ROOT = "CanadaGoose"
TURKEY_VULTURE_IMAGE_ROOT = "TurkeyVulture"
CICADA_IMAGE_ROOT = "Cicada"
CRICKET_IMAGE_ROOT = "Cricket"
FIREFLY_IMAGE_ROOT = "Firefly"
LUNA_MOTH_IMAGE_ROOT = "LunaMoth"
BLACK_WIDOW_IMAGE_ROOT = "Widow"
SALAMANDER_IMAGE_ROOT = "Salamander"
SNAPPING_TURTLE_IMAGE_ROOT = "SnappingTurtle"
AMERICAN_CROW_IMAGE_ROOT = "Crow"
RED_TAILED_HAWK_IMAGE_ROOT = "RedTailedHawk"
NIGHTHAWK_IMAGE_ROOT = "Nighthawk"
WOODCOCK_IMAGE_ROOT = "Woodcock"
SCREECH_OWL_IMAGE_ROOT = "ScreechOwl"
SNOWY_OWL_IMAGE_ROOT = "SnowyOwl"
BAT_IMAGE_ROOT = "Bat"
FLYING_SQUIRREL_IMAGE_ROOT = "FlyingSquirrel"
SKUNK_IMAGE_ROOT = "Skunk"
PORCUPINE_IMAGE_ROOT = "Porcupine"
COYOTE_IMAGE_ROOT = "Coyote"
MOUNTAIN_LION_IMAGE_ROOT = "MountainLion"

'''NATIONAL CREATURE DEX NUMBERS'''
DEER_DEX_NO = 1
SQUIRREL_DEX_NO = 2
RABBIT_DEX_NO = 3
CHIPMUNK_DEX_NO = 4
RACCOON_DEX_NO = 5
ROBIN_DEX_NO = 6
SPARROW_DEX_NO = 7
BLUEJAY_DEX_NO = 8
GOLDFINCH_DEX_NO = 9
CARDINAL_DEX_NO = 10
MONARCH_DEX_NO = 11
MANTIS_DEX_NO = 12
GARTERSNAKE_DEX_NO = 13
BOXTURTLE_DEX_NO = 14
TOAD_DEX_NO = 15
DUCK_DEX_NO = 16
TURKEY_DEX_NO = 17
GREAT_HORNED_OWL_DEX_NO = 18
EAGLE_DEX_NO = 19
OPOSSUM_DEX_NO = 20
REDFOX_DEX_NO = 21
BOBCAT_DEX_NO = 22
BLACKBEAR_DEX_NO = 23
MOOSE_DEX_NO = 24
WOLF_DEX_NO = 25

# Wave 2
CAT_DEX_NO = 26
MOUSE_DEX_NO = 27
GROUNDHOG_DEX_NO = 28
MOURNING_DOVE_DEX_NO = 29
CANADA_GOOSE_DEX_NO = 30
TURKEY_VULTURE_DEX_NO = 31
CICADA_DEX_NO = 32
CRICKET_DEX_NO = 33
FIREFLY_DEX_NO = 34
LUNA_MOTH_DEX_NO = 35
BLACK_WIDOW_DEX_NO = 36
SALAMANDER_DEX_NO = 37
SNAPPING_TURTLE_DEX_NO = 38
AMERICAN_CROW_DEX_NO = 39
_DEX_NO = 40
RED_TAILED_HAWK_DEX_NO = 40
NIGHTHAWK_DEX_NO = 41
WOODCOCK_DEX_NO = 42
SCREECH_OWL_DEX_NO = 43
SNOWY_OWL_DEX_NO = 44
BAT_DEX_NO = 45
FLYING_SQUIRREL_DEX_NO = 46
SKUNK_DEX_NO = 47
PORCUPINE_DEX_NO = 48
COYOTE_DEX_NO = 49
MOUNTAIN_LION_DEX_NO = 50

'''ENVIRONMENT DEX NUMBERS'''
EASTERN_US_FOREST_NO = 1
EVERGLADES_NO = 2

'''CREATURE KINGDOM NAMES'''
MAMMAL = "Mammal"
BIRD = "Bird"
REPTILE = "Reptile"
AMPHIBIAN = "Amphibian"
INSECT = "Insect"
FISH = "Fish"
MOLLUSK = "Mollusk"
CRUSTACEAN = "Crustacean"
ARACHNID = "Arachnid"

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

