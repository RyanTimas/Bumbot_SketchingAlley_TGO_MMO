from xml.dom import UserDataHandler

from src.database.handlers.QueryHandler import QueryHandler
from src.database.handlers.User_DatabaseHandler import UserDatabaseHandler
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.general_constants import *
from src.resources.db_queries import *


class TGOMMODatabaseHandler:
    def __init__(self, db_file):
        self.QueryHandler = QueryHandler(db_file=db_file)
        if RUN_TGOMMO_DB_INIT:
            self.init_tgommo_tables()


    ''' Insert Queries '''
    def insert_new_creature(self, params=(0,'', '', '', 0, 0, 0, 0, 0, 0, 0)):
        return self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_CREATURE, params=params)


    ''' Select Queries '''
    def get_creature(self, creature_id=0):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_CREATURE_BY_ID, params=(creature_id,))


    # Function to get creatures from a random environment
    def get_creatures_from_random_environment(self, environment_id=-1):
        if environment_id == -1:
            environment_id = self.QueryHandler.execute_query(TGOMMO_SELECT_RANDOM_ENVIRONMENT_ID, params=())

        response = self.QueryHandler.execute_query(TGOMMO_SELECT_CREATURES_FROM_SPECIFIED_ENVIRONMENT, params=(environment_id,))
        # todo convert to list of Creature objects
        return response


    def get_creature_id_by_dex_and_variant(self, dex_no, variant_no):
        response = self.QueryHandler.execute_query(
            TGOMMO_SELECT_CREATURE_ID_BY_DEX_AND_VARIANT_NO,
            params=(dex_no, variant_no)
        )
        return response[0] if response else None

    def get_environment_id_by_dex_and_variant(self, environment_dex_no, environment_variant_no):
        response = self.QueryHandler.execute_query(
            TGOMMO_SELECT_ENVIRONMENT_ID_BY_DEX_AND_VARIANT_NO,
            params=(environment_dex_no, environment_variant_no)
        )
        return response[0] if response else None

    ''' Update Queries '''
    ''' Delete Queries '''


    def init_tgommo_tables(self):
        # Create tables first
        self.QueryHandler.execute_query(TGOMMO_CREATE_CREATURE_TABLE)
        self.QueryHandler.execute_query(TGOMMO_CREATE_ENVIRONMENT_TABLE)
        self.QueryHandler.execute_query(TGOMMO_CREATE_ENVIRONMENT_CREATURE_TABLE)
        self.QueryHandler.execute_query(TGOMMO_CREATE_USER_CREATURE_TABLE)

        # Insert creature records
        creature_data = [
            #01 Deer
            ('Deer', 'Doe', 1, 1, 'White-Tailed Deer', 'Odocoileus virginianus', MAMMAL, '', DEER_IMAGE_FILE, 5),
            ('Deer', 'Buck', 1, 2, 'White-Tailed Deer', 'Odocoileus virginianus', MAMMAL, '', DEER_IMAGE_FILE, 5),

            #02 Squirrel
            ('Squirrel', '', 1, 1, 'Eastern Gray Squirrel', 'Sciurus carolinensis', MAMMAL, '', CHIPMUNK_IMAGE_FILE, 5),

            #04 Chipmunk
            ('Chipmunk', '', 4, 1, 'Eastern Chipmunk', 'Tamias striatus', MAMMAL, '', 'Chipmunk', 5),
        ]

        # Insert environment records
        environment_data = [
            # 01 Eastern US Forest
            ('Forest', 'Summer - Day', 1, 1, 'Eastern United States', '', 'forest_est', False, True, 5),
            ('Forest', 'Summer - Night', 1, 2, 'Eastern United States', '', 'forest_est', True, True, 5),
            ('Forest', 'Winter - Day', 1, 3, 'Eastern United States', '', 'forest_est', False, False, 5),
            ('Forest', 'Winter - Night', 1, 4, 'Eastern United States', '', 'forest_est', False, False, 5),

            # 02 Everglades
            ('Everglades', 'Day', 2, 1, 'Florida', '', 'everglades', False, True, 5),
            ('Everglades', 'Night', 2, 2, 'Florida', '', 'everglades', True, True, 5),
        ]

        for creature in creature_data:
            self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_CREATURE, params=creature)
        for environment in environment_data:
            self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_ENVIRONMENT, params=environment)

        # Link creatures to environments
        environment_creature_data = [
            # Forest - Day Spawns
            self.format_ce_link_params(DEER_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, TGOMMO_RARITY_COMMON, ''),
            self.format_ce_link_params(DEER_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, TGOMMO_RARITY_COMMON, ''),

            self.format_ce_link_params(CHIPMUNK_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, TGOMMO_RARITY_COMMON, '')
        ]

        for ec_link in environment_creature_data:
            self.QueryHandler.execute_query(TGOMMO_INSERT_ENVIRONMENT_CREATURE, params=ec_link)


    def format_ce_link_params(self, creature_dex_no, creature_variant_no, environment_dex_no, environment_variant_no, rarity, nickname=''):
        creature_info = self.get_creature_id_by_dex_and_variant(creature_dex_no, creature_variant_no)
        environment_info = self.get_environment_id_by_dex_and_variant(environment_dex_no, environment_variant_no)

        return (
            creature_info[0],
            environment_info[0],
            creature_info[1],
            environment_info[1],
            rarity,
            nickname
        )
