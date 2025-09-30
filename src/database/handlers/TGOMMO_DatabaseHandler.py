from src.database.handlers.QueryHandler import QueryHandler
from src.discord.objects.CreatureRarity import ALL_RARITIES, COMMON
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.discord.objects.TGOPlayer import TGOPlayer
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
        return_value = self.QueryHandler.execute_query(TGOMMO_INSERT_USER_CREATURE, params=params)
        return return_value[0][0]

    def insert_new_user_profile(self, user_id=-1, nickname = ''):
        params = (user_id, nickname, 1, 1, -1, -1, -1, -1, -1, -1, 0, 3, 1, 0,  1, 0)

        self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_USER_PROFILE, params=params)
        return self.get_user_profile_by_user_id(user_id=user_id)


    ''' SELECT QUERIES '''
    ''' Get Objects By IDs Queries'''
    def get_creature_by_id(self, creature_id=0, convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_CREATURE_BY_ID, params=(creature_id,))

        if convert_to_object:
            creature_details = response[0]
            return TGOCreature(creature_id=creature_details[0], name=creature_details[1], variant_name=creature_details[2], dex_no=creature_details[3], variant_no=creature_details[4], full_name=creature_details[5], scientific_name=creature_details[6], kingdom=creature_details[7], description=creature_details[8], img_root=creature_details[9], encounter_rate=creature_details[10])
        return response[0]

    def get_environment_by_id(self, environment_id=-1, convert_to_object=False):
        if environment_id == -1:
            environment_id = self.QueryHandler.execute_query(TGOMMO_SELECT_RANDOM_ENVIRONMENT_ID, params=())[0][0]

        response = self.QueryHandler.execute_query(TGOMMO_SELECT_ENVIRONMENT_BY_ID, params=(environment_id,))

        if convert_to_object:
            environment_details = response[0]
            return TGOEnvironment(environment_id=environment_details[0], name=environment_details[1], variant_name=environment_details[2], dex_no=environment_details[3], variant_no=environment_details[4], location=environment_details[5], description=environment_details[6], img_root=environment_details[7], is_night_environment=environment_details[8], in_circulation=environment_details[9], encounter_rate=environment_details[10])
        return response[0]

    def get_user_profile_by_user_id(self, user_id=0, convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_USER_PROFILE_BY_ID, params=(user_id,))

        if convert_to_object:
            player_details = response[0]
            return TGOPlayer(player_id=player_details[0], user_id=player_details[1], nickname=player_details[2], avatar_id=player_details[3], background_id=player_details[4], creature_slot_id_1=player_details[5], creature_slot_id_2=player_details[6], creature_slot_id_3=player_details[7], creature_slot_id_4=player_details[8],  creature_slot_id_5=player_details[9],creature_slot_id_6=player_details[10],currency=player_details[11], available_catches=player_details[12],rod_level=player_details[13], rod_amount=player_details[14], trap_level=player_details[15],trap_amount=player_details[16])
        return response[0]

    def get_creature_by_catch_id(self, creature_id=0, convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_CREATURE_BY_CATCH_ID, params=(creature_id,))

        if not response:
            return None

        if convert_to_object:
            creature_details = response[0]
            return TGOCreature(creature_id=creature_details[0], name=creature_details[1], variant_name=creature_details[2], dex_no=creature_details[3], variant_no=creature_details[4], full_name=creature_details[5], scientific_name=creature_details[6], kingdom=creature_details[7], description=creature_details[8], img_root=creature_details[9], encounter_rate=creature_details[10])
        return response[0]


    ''' Get Objects By Dex No Queries'''
    def get_creature_by_dex_and_variant_no(self, dex_no=0, variant_no=1, convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_CREATURE_BY_DEX_AND_VARIANT_NUMBER, params=(dex_no, variant_no))

        if convert_to_object:
            creature_details = response[0]
            return TGOCreature(creature_id=creature_details[0], name=creature_details[1], variant_name=creature_details[2], dex_no=creature_details[3], variant_no=creature_details[4], full_name=creature_details[5], scientific_name=creature_details[6], kingdom=creature_details[7], description=creature_details[8], img_root=creature_details[9], encounter_rate=creature_details[10])
        return response[0]

    def get_environment_by_dex_and_variant_no(self, dex_no=0, variant_no=1, convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_ENVIRONMENT_BY_DEX_AND_VARIANT_NUMBER, params=(dex_no, variant_no))

        if convert_to_object:
            environment_details = response[0]
            return TGOEnvironment(environment_id=environment_details[0], name=environment_details[1], variant_name=environment_details[2], dex_no=environment_details[3], variant_no=environment_details[4], location=environment_details[5], description=environment_details[6], img_root=environment_details[7], is_night_environment=environment_details[8], in_circulation=environment_details[9], encounter_rate=environment_details[10])
        return response[0]


    ''' Other Get Object Queries '''
    # Returns all creatures found within a particular environment
    def get_creatures_from_environment(self, environment_id=-1, convert_to_object=False):
        if environment_id == -1:
            environment_id = self.QueryHandler.execute_query(TGOMMO_SELECT_RANDOM_ENVIRONMENT_ID, params=())[0][0]

        response = self.QueryHandler.execute_query(TGOMMO_SELECT_CREATURES_FROM_SPECIFIED_ENVIRONMENT, params=(environment_id,))
        return response

    def get_all_creatures_caught_by_user(self, user_id=0, include_variants=False, is_server_page=False, include_mythics=False):
        creatures = self.QueryHandler.execute_query(TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_SERVER if is_server_page else TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_USER, params=(() if is_server_page else (user_id,)))

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
                    if creatures[first_idx][catch_signifier] == 0 and len(creatures[first_idx]) == 8:
                        creatures[first_idx].append([])
                        for creature in creatures:
                            if creature[3] == creature_dex_no and creature[catch_signifier] > 0:
                                creatures[first_idx][8].append(creature[4])
                        if len(creatures[first_idx][8]) == 0:
                            creatures[first_idx].pop(8)

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

    def get_creature_rarity_for_environment(self, creature_id=0, environment_id=0):
        response = self.QueryHandler.execute_query(TGOMMO_GET_RARITY_FOR_CREATURE_BY_CREATURE_ID_AND_ENVIRONMENT_ID, params=(creature_id, environment_id,))

        for rarity in ALL_RARITIES:
            if rarity.name == response[0][0]:
                return rarity
        return COMMON

    # Get all display creatures for a player profile page
    def get_creatures_for_player_profile(self, params=(-1,-1,-1,-1,-1,-1)):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_DISPLAY_CREATURES_FOR_PLAYER_PROFILE_PAGE, params=params)
        return response

    # Get all creatures a user has caught
    def get_creature_collection_by_user(self, user_id=0, convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_GET_CREATURE_COLLECTION_BY_USER, params=(user_id,))
        return response


    ''' Encyclopedia & Statistics Queries '''
    def get_total_user_catches_for_species(self, user_id=0, dex_no=0, variant_no=0):
        response = self.QueryHandler.execute_query(TGOMMO_GET_COUNT_FOR_USER_CATCHES_FOR_CREATURE_BY_DEX_NUM, params=(user_id, dex_no))
        return response[0][0]

    def get_total_server_catches_for_species(self, creature_id=0):
        response = self.QueryHandler.execute_query(TGOMMO_GET_COUNT_FOR_SERVER_CATCHES_FOR_CREATURE_BY_CREATURE_ID,params=(creature_id,))
        return response[0][0]

    # Check if mythics have been unlocked on the server yet
    def get_server_mythical_count(self):
        response = self.QueryHandler.execute_query(TGOMMO_GET_SERVER_MYTHICAL_COUNT, params=())
        return response[0][0]

    def get_total_catches_by_user(self, user_id=0):
        response = self.QueryHandler.execute_query(TGOMMO_GET_TOTAL_CATCHES_BY_USER_ID, params=(user_id,))
        return response[0][0]

    # Gets encyclopedia page info for a user or server page
    def get_encyclopedia_page_info(self, user_id=0, is_server_page=False, include_variants=False, include_mythics=False):
        if include_variants:
            query = TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_USER_BY_ID if not is_server_page else TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_SERVER_BY_ID
        else:
            query = TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_USER_BY_DEX_NUM if not is_server_page else TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_SERVER_BY_DEX_NUM

        params = (user_id, include_mythics) if not is_server_page else (include_mythics,)

        return self.QueryHandler.execute_query(query, params=params)[0]

    def get_ids_for_unique_creatures(self):
        response = self.QueryHandler.execute_query(TGOMMO_GET_IDS_FOR_UNIQUE_CREATURES, params=())
        return response[0]


    ''' Update Queries '''
    def update_creature_nickname(self, creature_id, nickname):
        response = self.QueryHandler.execute_query(TGOMMO_UPDATE_CREATURE_NICKNAME_BY_CATCH_ID, params=(nickname, creature_id))
        return response

    def update_user_profile(self, params=( '', 1, 1, -1, -1, -1, -1, -1, -1, 0, 3, 1, 0,  1, 0, -1)):
        response = self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_PROFILE, params=params)
        return response

    def update_user_profile_display_name(self, user_id, nickname):
        response = self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_PROFILE_NICKNAME, params=(nickname, user_id))
        return response

    def update_user_profile_creature(self, user_id, creature_id, creature_number):
        # check to make sure creature is not already featured on user profile
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_USER_PROFILE_BY_ID, params=(user_id))

        # Check if creature is already in any slot
        for slot in (10, 11, 12, 13, 14, 15):
            if response[0][slot] == creature_id:
                return False

        query_map = (
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_1,
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_2,
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_3,
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_4,
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_5,
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_6
        )

        response = self.QueryHandler.execute_query(query_map[creature_number], params=(creature_id, user_id))
        return True if response else False

    def update_user_profile_display_creature_slots(self, params = (-1, -1, -1, -1, -1, -1, -1)):
        response = self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_DISPLAY_CREATURES, params=params)
        return response

    def update_creature_display_index(self, user_id, creature_id, display_index):
        queries = [
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_1,
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_2,
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_3,
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_4,
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_5,
            TGOMMO_UPDATE_USER_PROFILE_CREATURE_6
        ]

        response = self.QueryHandler.execute_query(queries[display_index], params=(creature_id, user_id))
        return response

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
        self.QueryHandler.execute_query(TGOMMO_CREATE_USER_PROFILE_TABLE)

        # Insert creature records
        creature_data = [
            # WAVE 1
            ('Deer', 'Doe', 1, 1, 'White-Tailed Deer', 'Odocoileus virginianus', MAMMAL, '', DEER_IMAGE_ROOT, 5),
            ('Deer', 'Buck', 1, 2, 'White-Tailed Deer', 'Odocoileus virginianus', MAMMAL, '', DEER_IMAGE_ROOT, 5),
            ('Squirrel', '', 2, 1, 'Eastern Gray Squirrel', 'Sciurus carolinensis', MAMMAL, '', SQUIRREL_IMAGE_ROOT, 5),
            ('Rabbit', '', 3, 1, 'Eastern Cottontail', 'Sylvilagus floridanus', MAMMAL, '', RABBIT_IMAGE_ROOT, 5),
            ('Chipmunk', '', 4, 1, 'Eastern Chipmunk', 'Tamias striatus', MAMMAL, '', CHIPMUNK_IMAGE_ROOT, 5),
            ('Raccoon', '', 5, 1, 'Raccoon', 'Procyon lotor', MAMMAL, '', RACOON_IMAGE_ROOT, 5),
            ('Robin', '', 6, 1, 'American Robin', 'Turdus migratorius', BIRD, '', ROBIN_IMAGE_ROOT, 5),
            ('Sparrow', 'Male', 7, 1, 'House Sparrow', 'Passer domesticus', BIRD, '', SPARROW_IMAGE_ROOT, 5),
            ('Sparrow', 'Female', 7, 2, 'House Sparrow', 'Passer domesticus', BIRD, '', SPARROW_IMAGE_ROOT, 5),
            ('Blue Jay', '', 8, 1, 'Blue Jay', 'Cyanocitta cristata', BIRD, '', BLUEJAY_IMAGE_ROOT, 5),
            ('Goldfinch', '', 9, 1, 'American Goldfinch', 'Spinus tristis', BIRD, '', GOLDFINCH_IMAGE_ROOT, 5),
            ('Cardinal', 'Male', 10, 1, 'Northern Cardinal', 'Cardinalis cardinalis', BIRD, '', CARDINAL_IMAGE_ROOT, 5),
            ('Cardinal', 'Female', 10, 2, 'Northern Cardinal', 'Cardinalis cardinalis', BIRD, '', CARDINAL_IMAGE_ROOT, 5),
            ('Monarch', 'Caterpillar', 11, 1, 'Monarch', 'Danaus plexippus', INSECT, '', MONARCH_IMAGE_ROOT, 5),
            ('Monarch', 'Chrysalis', 11, 2, 'Monarch', 'Danaus plexippus', INSECT, '', MONARCH_IMAGE_ROOT, 5),
            ('Monarch', 'Butterfly', 11, 3, 'Monarch', 'Danaus plexippus', INSECT, '', MONARCH_IMAGE_ROOT, 5),
            ('Mantis', '', 12, 1, 'Praying Mantis', 'Stagmomantis carolina', INSECT, '', MANTIS_IMAGE_ROOT, 5),
            ('Snake', '', 13, 1, 'Eastern Garter Snake', 'Thamnophis sirtalis sirtalis', REPTILE, '', GARTERSNAKE_IMAGE_ROOT, 5),
            ('Turtle', '', 14, 1, 'Box Turtle', 'Terrapene carolina carolina', REPTILE, '', TURTLE_IMAGE_ROOT, 5),
            ('Toad', '', 15, 1, 'American Toad', 'Anaxyrus americanus', AMPHIBIAN, '', TOAD_IMAGE_ROOT, 5),
            ('Duck', 'Drake', 16, 1, 'Mallard', 'Anas platyrhynchos', BIRD, '', MALLARD_IMAGE_ROOT, 5),
            ('Duck', 'Hen', 16, 2, 'Mallard', 'Anas platyrhynchos', BIRD, '', MALLARD_IMAGE_ROOT, 5),
            ('Turkey', '', 17, 1, 'Wild Turkey', 'Meleagris gallopavo', BIRD, '', TURKEY_IMAGE_ROOT, 5),
            ('Owl', '', 18, 1, 'Great Horned Owl', 'Bubo virginianus', BIRD, '', OWL_IMAGE_ROOT, 5),
            ('Eagle', '', 19, 1, 'Bald Eagle', 'Haliaeetus leucocephalus', BIRD, '', EAGLE_IMAGE_ROOT, 5),
            ('Opossum', '', 20, 1, 'Virginia Opossum', 'Didelphis virginiana', MAMMAL, '', OPOSSUM_IMAGE_ROOT, 5),
            ('Fox', '', 21, 1, 'Red Fox', 'Vulpes vulpes', MAMMAL, '', REDFOX_IMAGE_ROOT, 5),
            ('Bobcat', '', 22, 1, 'Bobcat', 'Lynx rufus', MAMMAL, '', BOBCAT_IMAGE_ROOT, 5),
            ('Bear', '', 23, 1, 'Black Bear', 'Ursus americanus', MAMMAL, '', BLACKBEAR_IMAGE_ROOT, 5),
            ('Moose', 'Cow', 24, 1, 'Moose', 'Alces alces', MAMMAL, '', MOOSE_IMAGE_ROOT, 5),
            ('Moose', 'Bull', 24, 2, 'Moose', 'Alces alces', MAMMAL, '', MOOSE_IMAGE_ROOT, 5),
            ('Wolf', '', 25, 1, 'Gray Wolf', 'Canis lupus', MAMMAL, '', WOLF_IMAGE_ROOT, 5),

            # WAVE 2
            ('Mouse', '', 26, 1, 'Field Mouse', 'Apodemus', MAMMAL, '', MOUSE_IMAGE_ROOT, 5),
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
            self.format_creature_environment_link_params(DEER_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, ''),
            self.format_creature_environment_link_params(DEER_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, ''),
            self.format_creature_environment_link_params(SQUIRREL_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, ''),
            self.format_creature_environment_link_params(RABBIT_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, ''),
            self.format_creature_environment_link_params(CHIPMUNK_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, ''),
            self.format_creature_environment_link_params(RACCOON_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, ''),
            self.format_creature_environment_link_params(ROBIN_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, ''),
            self.format_creature_environment_link_params(SPARROW_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, ''),
            self.format_creature_environment_link_params(SPARROW_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, ''),
            self.format_creature_environment_link_params(BLUEJAY_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, ''),
            self.format_creature_environment_link_params(GOLDFINCH_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, ''),
            self.format_creature_environment_link_params(CARDINAL_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, ''),
            self.format_creature_environment_link_params(CARDINAL_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, ''),
            self.format_creature_environment_link_params(MONARCH_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, ''),
            self.format_creature_environment_link_params(MONARCH_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, ''),
            self.format_creature_environment_link_params(MONARCH_DEX_NO, 3, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_RARE, ''),
            self.format_creature_environment_link_params(MANTIS_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_RARE, ''),
            self.format_creature_environment_link_params(GARTERSNAKE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, ''),
            self.format_creature_environment_link_params(BOXTURTLE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_RARE, ''),
            self.format_creature_environment_link_params(TOAD_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, ''),
            self.format_creature_environment_link_params(DUCK_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, ''),
            self.format_creature_environment_link_params(DUCK_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, ''),
            self.format_creature_environment_link_params(TURKEY_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_RARE, ''),
            self.format_creature_environment_link_params(EAGLE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_EPIC, ''),
            self.format_creature_environment_link_params(OWL_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_EPIC, ''),
            self.format_creature_environment_link_params(OPOSSUM_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, ''),
            self.format_creature_environment_link_params(REDFOX_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_RARE, ''),
            self.format_creature_environment_link_params(BOBCAT_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_RARE, ''),
            self.format_creature_environment_link_params(BLACKBEAR_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_EPIC, ''),
            self.format_creature_environment_link_params(MOOSE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_LEGENDARY, ''),
            self.format_creature_environment_link_params(MOOSE_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_LEGENDARY, ''),
            self.format_creature_environment_link_params(WOLF_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_LEGENDARY, ''),

            # Forest - Night Spawns
            self.format_creature_environment_link_params(MOUSE_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, ''),
            self.format_creature_environment_link_params(RACCOON_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_COMMON, ''),
        ]

        for ec_link in environment_creature_data:
            self.QueryHandler.execute_query(TGOMMO_INSERT_ENVIRONMENT_CREATURE, params=ec_link)


    def format_creature_environment_link_params(self, creature_dex_no, creature_variant_no, environment_dex_no, environment_variant_no, spawn_time, rarity, local_name=''):
        creature_info = self.get_creature_by_dex_and_variant_no(creature_dex_no, creature_variant_no)
        environment_info = self.get_environment_by_dex_and_variant_no(environment_dex_no, environment_variant_no)

        return (
            creature_info[0],
            environment_info[0],
            spawn_time,
            creature_info[1],
            environment_info[1],
            rarity,
            local_name
        )