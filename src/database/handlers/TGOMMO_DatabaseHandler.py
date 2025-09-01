from xml.dom import UserDataHandler

from src.database.handlers.QueryHandler import QueryHandler
from src.discord.objects.CreatureRarity import ALL_RARITIES, COMMON
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

    def insert_new_user_creature(self, params=(0,0,0,0,0)):
        return self.QueryHandler.execute_query(TGOMMO_INSERT_USER_CREATURE, params=params)


    ''' Select Queries '''
    def get_creature_by_id(self, creature_id=0):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_CREATURE_BY_DEX_AND_VARIANT_NUMBER, params=(creature_id,))
        return response[0]


    def get_environment_by_id(self, environment_id=0):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_ENVIRONMENT_BY_DEX_AND_VARIANT_NUMBER, params=(environment_id,))
        return response[0]


    def get_creature_by_dex_and_variant_no(self, dex_no=0, variant_no=1):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_CREATURE_BY_DEX_AND_VARIANT_NUMBER, params=(dex_no, variant_no))
        return response[0]


    def get_environment_by_dex_and_variant_no(self, dex_no=0, variant_no=1):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_ENVIRONMENT_BY_DEX_AND_VARIANT_NUMBER, params=(dex_no, variant_no))
        return response[0]


    def get_total_user_catches_for_species(self, user_id=0, dex_no=0, variant_no=0):
        response = self.QueryHandler.execute_query(TGOMMO_GET_COUNT_FOR_USER_CATCHES_FOR_CREATURE_BY_DEX_NUM, params=(user_id, dex_no))
        return response[0][0]


    def get_total_server_catches_for_species(self, creature_id=0):
        response = self.QueryHandler.execute_query(TGOMMO_GET_COUNT_FOR_SERVER_CATCHES_FOR_CREATURE_BY_CREATURE_ID,params=(creature_id,))
        return response[0][0]


    # Returns all creatures found within a particular environment
    def get_creatures_from_environment(self, environment_id=-1):
        if environment_id == -1:
            environment_id = self.QueryHandler.execute_query(TGOMMO_SELECT_RANDOM_ENVIRONMENT_ID, params=())

        response = self.QueryHandler.execute_query(TGOMMO_SELECT_CREATURES_FROM_SPECIFIED_ENVIRONMENT, params=(environment_id,))
        return response


    def get_all_creatures_caught_by_user(self, user_id=0, include_variants=False, include_mythics=False):
        creatures = self.QueryHandler.execute_query(TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_USER, params=(user_id,))

        if not include_variants:
            seen_ids = {}  # Track creature IDs we've seen and their first index
            i = 0
            while i < len(creatures):
                creature_dex_no = creatures[i][3]

                if creature_dex_no in seen_ids:
                    # We've seen this ID before, add counts to the first occurrence
                    first_idx = seen_ids[creature_dex_no]

                    creatures[first_idx] = list(creatures[first_idx])  # Convert tuple to list for modification

                    # logic to handle when a user has one variant but not the 0th variant
                    catch_signifier = 6 if include_mythics else 5
                    if creatures[first_idx][catch_signifier] == 0 and len(creatures[first_idx]) == 7:
                        creatures[first_idx].append([])
                        for creature in creatures:
                            if creature[3] == creature_dex_no and creature[catch_signifier] > 0:
                                creatures[first_idx][7].append(creature[4])
                        if len(creatures[first_idx][7]) == 0:
                            creatures[first_idx].pop(7)

                    creatures[first_idx][5] += creatures[i][5]
                    creatures[first_idx][6] += creatures[i][6]
                    creatures[first_idx] = tuple(creatures[first_idx])  # Convert back to tuple

                    # Remove this duplicate
                    creatures.pop(i)
                else:
                    # First time seeing this ID, record its position
                    seen_ids[creature_dex_no] = i
                    i += 1

        return creatures


    def get_total_catches_by_user(self, user_id=0):
        response = self.QueryHandler.execute_query(TGOMMO_GET_TOTAL_CATCHES_BY_USER_ID, params=(user_id,))
        return response[0][0]


    def get_encyclopedia_page_info(self, user_id=0, is_server_page=False, include_variants=False):

        if include_variants:
            query = TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_USER_BY_ID if not is_server_page else TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_SERVER_BY_ID
        else:
            query = TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_USER_BY_DEX_NUM if not is_server_page else TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_SERVER_BY_DEX_NUM

        params = (user_id,) if not is_server_page else ()

        return self.QueryHandler.execute_query(query, params=params)[0]


    def get_creature_rarity_for_environment(self, creature_id=0, environment_id=0):
        response = self.QueryHandler.execute_query(TGOMMO_GET_RARITY_FOR_CREATURE_BY_CREATURE_ID_AND_ENVIRONMENT_ID, params=(creature_id, environment_id,))

        for rarity in ALL_RARITIES:
            if rarity.name == response[0][0]:
                return rarity
        return COMMON


    def get_ids_for_unique_creatures(self):
        response = self.QueryHandler.execute_query(TGOMMO_GET_IDS_FOR_UNIQUE_CREATURES, params=())
        return response[0]


    ''' Update Queries '''
    ''' Delete Queries '''


    '''"""""""""""""""""""""""""""""'''
    ''' Initialization Of DB Tables '''
    '''"""""""""""""""""""""""""""""'''
    def init_tgommo_tables(self):
        # Create tables first
        self.QueryHandler.execute_query(TGOMMO_CREATE_CREATURE_TABLE)
        self.QueryHandler.execute_query(TGOMMO_CREATE_ENVIRONMENT_TABLE)
        self.QueryHandler.execute_query(TGOMMO_CREATE_ENVIRONMENT_CREATURE_TABLE)
        self.QueryHandler.execute_query(TGOMMO_CREATE_USER_CREATURE_TABLE)

        # Insert creature records
        creature_data = [
            #01 Deer
            ('Deer', 'Doe', 1, 1, 'White-Tailed Deer', 'Odocoileus virginianus', MAMMAL, '', DEER_IMAGE_ROOT, 5),
            ('Deer', 'Buck', 1, 2, 'White-Tailed Deer', 'Odocoileus virginianus', MAMMAL, '', DEER_IMAGE_ROOT, 5),

            #02 Squirrel
            ('Squirrel', '', 1, 1, 'Eastern Gray Squirrel', 'Sciurus carolinensis', MAMMAL, '', CHIPMUNK_IMAGE_ROOT, 5),

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
        creature_info = self.get_creature_by_dex_and_variant_no(creature_dex_no, creature_variant_no)
        environment_info = self.get_environment_by_dex_and_variant_no(environment_dex_no, environment_variant_no)

        return (
            creature_info[0],
            environment_info[0],
            creature_info[1],
            environment_info[1],
            rarity,
            nickname
        )