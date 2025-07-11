import configparser
import os

# set up config
CONFIG_NAME = 'config_local.ini'
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), f"configs\\{CONFIG_NAME}")

config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)

'''*****************'''
'''Bot Launch Constants'''
'''*****************'''
RUN_DISCORD_BOT = config.getboolean('General', 'RUN_DISCORD_BOT', fallback=False)
RUN_TWITCH_BOT = config.getboolean('General', 'RUN_TWITCH_BOT', fallback=False)
RUN_OBS_BOT = config.getboolean('General', 'RUN_OBS_WEBSOCKET', fallback=False)

'''*****************'''
'''Discord constants'''
'''*****************'''
DISCORD_TOKEN = config['DISCORD']['DISCORD_TOKEN']

'''*************'''
'''OBS Constants'''
'''*************'''
OBS_HOST = config['OBSWebsocket']['OBS_HOST']
OBS_PORT = config.getint('OBSWebsocket', 'OBS_PORT', fallback=4455)
OBS_PASSWORD = config['OBSWebsocket']['OBS_PASSWORD']

'''****************'''
'''Twitch Constants'''
'''****************'''
TWITCH_CLIENT_ID = config['Twitch']['TWITCH_CLIENT_ID']
TWITCH_APP_SECRET = config['Twitch']['TWITCH_APP_SECRET']
TWITCH_TARGET_CHANNEL = config['Twitch']['TWITCH_TARGET_CHANNEL']
ACCESS_TOKEN = config['Twitch']['TWITCH_ACCESS_TOKEN']
REFRESH_TOKEN = config['Twitch']['TWITCH_REFRESH_TOKEN']


