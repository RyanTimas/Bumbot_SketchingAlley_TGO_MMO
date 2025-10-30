import configparser
import os
from datetime import time

# set up config
CONFIG_NAME = 'config_local.ini'
#CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), f"configs\\{CONFIG_NAME}")
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "configs", CONFIG_NAME)

config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)

'''*****************'''
'''Bot Launch Constants'''
'''*****************'''
RUN_DISCORD_BOT = config.getboolean('General', 'RUN_DISCORD_BOT', fallback=False)
RUN_TWITCH_BOT = config.getboolean('General', 'RUN_TWITCH_BOT', fallback=False)
RUN_OBS_BOT = config.getboolean('General', 'RUN_OBS_WEBSOCKET', fallback=False)

RUN_SA_DB_INIT = config.getboolean('General', 'RUN_SA_DB_INIT', fallback=False)
RUN_TGOMMO_DB_INIT = config.getboolean('General', 'RUN_TGOMMO_DB_INIT', fallback=False)

'''*****************'''
'''Discord constants'''
'''*****************'''
DISCORD_TOKEN = config['DISCORD']['DISCORD_TOKEN']
DISCORD_DATABASE = config['DISCORD']['DISCORD_DATABASE']

'''sketching alley channels'''
DISCORD_SA_CHANNEL_ID_GENERAL = 816147864026742807
DISCORD_SA_CHANNEL_ID_HEY_YOU = 816147864026742805
DISCORD_SA_CHANNEL_ID_PLAYER_STATS = 816147864026742804
DISCORD_SA_CHANNEL_ID_TGOMMO = 1411159094538014833

DISCORD_SA_CHANNEL_ID_TEST = 1196630996477542570
DISCORD_BV_CHANNEL_ID_TEST = 1279894623535497268
DISCORD_BV_CHANNEL_ID_TEST_2 = 1432547947849187349

TGOMMO_ROLE_ID = 1430628300216205332
TGOMMO_ROLE = f"<@&{TGOMMO_ROLE_ID}>"

'''sketching alley user ids'''
BUMBISS_USER_ID = 801108873955115028
JORDO_USER_ID = 667807803418607651

USER_WHITELIST = [BUMBISS_USER_ID]

'''**********************'''
'''File Paths / Locations'''
'''**********************'''
IMAGE_FOLDER_BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "")
IMAGE_FOLDER_IMAGES = "images"
IMAGE_FOLDER_FONTS = "fonts"


'''*****************'''
'''General Constants'''
'''*****************'''
DIVIDER_LINE = "──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────"

NEW_DAY_TIMESTAMP = time(0, 0)  # 00:00:00



