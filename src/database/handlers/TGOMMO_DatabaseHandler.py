from src.database.handlers.QueryHandler import QueryHandler
from src.discord.objects.CreatureRarity import ALL_RARITIES, COMMON, get_rarity_by_name
from src.discord.objects.TGOAvatar import TGOAvatar
from src.discord.objects.TGOCollection import TGOCollection
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.discord.objects.TGOPlayer import TGOPlayer
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.queries.avatar_quest_db_queries import *
from src.resources.constants.general_constants import *
from src.resources.constants.queries.create_table_queries import *
from src.resources.constants.queries.db_queries import *


class TGOMMODatabaseHandler:
    def __init__(self, db_file):
        self.QueryHandler = QueryHandler(db_file=db_file)
        if RUN_TGOMMO_DB_INIT:
            self.init_tgommo_tables()


    def execute_query(self, query, params=()):
        return self.QueryHandler.execute_query(query, params=params)


    ''' Insert Queries '''
    def insert_new_creature(self, params=(0,'', '', '', 0, 0, 0, 0, 0, 0, 0)):
        return self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_CREATURE, params=params)

    def insert_new_user_creature(self, params=(0,0,0,0,0)):
        return_value = self.QueryHandler.execute_query(TGOMMO_INSERT_USER_CREATURE, params=params)
        return return_value[0][0]

    def insert_new_user_profile(self, user_id=-1, nickname = ''):
        params = (user_id, nickname, 'D1', 1, -1, -1, -1, -1, -1, -1, 0, 3, 1, 0,  1, 0)

        self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_USER_PROFILE, params=params)
        return self.get_user_profile_by_user_id(user_id=user_id)

    ''' Avatar Queries '''
    def insert_new_user_profile_avatar_link(self, user_id=-1, avatar_id=-1):
        return self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_USER_AVATAR_LINK, params=(avatar_id, user_id))

    def unlock_avatar_for_server(self, avatar_id=-1):
        return self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_AVATAR_UNLOCK_STATUS, params=(-1, avatar_id))

    def check_if_user_unlocked_avatar(self, user_id=-1, avatar_id=-1):
        return self.QueryHandler.execute_query(TGOMMO_AVATAR_IS_UNLOCKED_FOR_PLAYER, params=(user_id, avatar_id))[0][0] > 0


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

    def get_user_profile_by_user_id(self, user_id=0, convert_to_object=False, nickname=None):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_USER_PROFILE_BY_ID, params=(user_id,))
        if response is None or len(response) == 0:
            self.insert_new_user_profile(user_id=user_id)
            response = self.QueryHandler.execute_query(TGOMMO_SELECT_USER_PROFILE_BY_ID, params=(user_id,))

        if convert_to_object:
            player_details = response[0]

            avatar_details = self.QueryHandler.execute_query(TGOMMO_SELECT_AVATAR_BY_ID, params=(player_details[3],))[0]
            avatar = TGOAvatar(avatar_num=avatar_details[0], avatar_id=avatar_details[1], name=avatar_details[2], avatar_type=avatar_details[3], img_root=avatar_details[4], series=avatar_details[5],) if avatar_details else None
            return TGOPlayer(player_id=player_details[0], user_id=player_details[1], nickname=player_details[2], avatar=avatar, background_id=player_details[4], creature_slot_id_1=player_details[5], creature_slot_id_2=player_details[6], creature_slot_id_3=player_details[7], creature_slot_id_4=player_details[8],  creature_slot_id_5=player_details[9],creature_slot_id_6=player_details[10],currency=player_details[11], available_catches=player_details[12],rod_level=player_details[13], rod_amount=player_details[14], trap_level=player_details[15],trap_amount=player_details[16])
        return response[0]

    def get_creature_by_catch_id(self, creature_id=0, convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_USER_CREATURE_BY_CATCH_ID, params=(creature_id,))

        if not response:
            return None

        if convert_to_object:
            creature_info = response[0]

            return TGOCreature(
                creature_id=creature_info[1],
                catch_id=creature_info[0],

                name=creature_info[2],
                local_name = creature_info[3],
                nickname=creature_info[4],
                variant_name = creature_info[5],

                dex_no=creature_info[6],
                variant_no=creature_info[7],

                full_name=creature_info[8],
                scientific_name=creature_info[9],
                kingdom=creature_info[10],
                description=creature_info[11],

                img_root=creature_info[12],
                sub_environment=creature_info[13],
                encounter_rate=creature_info[14],
                rarity= get_rarity_by_name(creature_info[15]),

                caught_date=creature_info[16],
            )
        return response[0]

    def get_avatar_by_id(self, avatar_id, convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_AVATAR_BY_ID, params=(avatar_id,))

        if convert_to_object:
            avatar_details = response[0]
            return TGOAvatar(avatar_num=avatar_details[0], avatar_id=avatar_details[1], name=avatar_details[2], avatar_type=avatar_details[3], img_root=avatar_details[4], series=avatar_details[5])
        return response[0]

    def get_unlocked_avatars_by_user_id(self, user_id, convert_to_object=False):
        avatar_details = self.QueryHandler.execute_query(TGOMMO_AVATAR_GET_UNLOCKED_AVATARS_BY_USER_ID_ORDERED_BY_AVATAR_TYPE, params=(user_id,))

        if convert_to_object:
            avatars = []
            for avatar_details in avatar_details:
                avatar = TGOAvatar(avatar_num=avatar_details[0], avatar_id=avatar_details[1], name=avatar_details[2], avatar_type=avatar_details[3], img_root=avatar_details[4], series=avatar_details[5])
                avatars.append(avatar)
            return avatars
        return avatar_details

    def get_unlocked_avatars_for_server(self, convert_to_object=False):
        all_avatar_details = self.QueryHandler.execute_query(TGOMMO_AVATAR_GET_UNLOCKED_AVATARS_BY_USER_ID, params=(-1,))

        if convert_to_object:
            avatars = []
            for avatar_details in all_avatar_details:
                avatar = TGOAvatar(avatar_num=avatar_details[0], avatar_id=avatar_details[1], name=avatar_details[2], avatar_type=avatar_details[3], img_root=avatar_details[4], is_unlocked=bool(avatar_details[5]))
                avatars.append(avatar)
            return avatars
        return all_avatar_details

    def get_unlocked_avatar_ids_for_server(self):
        response = self.QueryHandler.execute_query(TGOMMO_AVATAR_GET_UNLOCKED_AVATARS_BY_USER_ID, params=(-1,))
        return [row[1] for row in response]

    def get_avatar_unlock_conditions(self, convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_GET_ALL_AVATAR_UNLOCK_CONDITIONS, params=())

        if convert_to_object:
            avatars = []
            for avatar_details in response:
                avatar = TGOAvatar(avatar_num=-1, avatar_id=avatar_details[0], name=avatar_details[1],avatar_type=AVATAR_TYPE_SECRET, img_root=avatar_details[2],unlock_query=avatar_details[3], unlock_threshold=avatar_details[4], is_parent_entry=avatar_details[5], is_secret=avatar_details[6])
                avatars.append(avatar)
            return avatars
        return response


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

    def get_all_creatures_caught_for_encyclopedia(self, user_id=0, include_variants=False, is_server_page=False, include_mythics=False, environment_id=0, environment_variant_no=0):
        # determine whether we should grab creatures for a specific environment or all environments
        if environment_variant_no > 0:
            query = TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_SERVER_FOR_ENVIRONMENT_DEX_NO_AND_VARIANT_NO if is_server_page else TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_USER_BY_DEX_NUM_AND_VARIANT_NO
            params = (user_id, environment_id, environment_variant_no) if not is_server_page else (environment_id, environment_variant_no)
        elif environment_id > 0:
            query = TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_SERVER_FOR_ENVIRONMENT_DEX_NO if is_server_page else TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_USER_BY_DEX_NUM
            params = (user_id, environment_id) if not is_server_page else (environment_id,)
        else:
            query = TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_SERVER if is_server_page else TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_USER
            params = (user_id,) if not is_server_page else ()

        creatures = self.QueryHandler.execute_query(query, params=params)

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

    def get_creature_rarity_for_environment(self, creature_id=0, environment_id=None, dex_no=None):
        query = TGOMMO_GET_RARITY_FOR_CREATURE_BY_CREATURE_ID_AND_ENVIRONMENT_ID if environment_id is not None else TGOMMO_GET_RARITY_FOR_CREATURE_BY_CREATURE_ID_AND_ENVIRONMENT_DEX_NO
        params = (creature_id, environment_id) if environment_id is not None else (creature_id, dex_no)
        response = self.QueryHandler.execute_query(query, params=params)

        for rarity in ALL_RARITIES:
            if rarity.name == response[0][0]:
                return rarity
        return COMMON

    # Get all display creatures for a player profile page
    def get_creatures_for_player_profile(self, params=(-1,-1,-1,-1,-1,-1)):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_DISPLAY_CREATURES_FOR_PLAYER_PROFILE_PAGE, params=params)
        return response

    def get_creature_for_player_profile(self, creature_id=(-1)):
        response = self.QueryHandler.execute_query(TGOMMO_SELECT_DISPLAY_CREATURE_FOR_PLAYER_PROFILE_PAGE, params=(creature_id,))
        return response[0]

    # Get all creatures a user has caught
    def get_creature_collection_by_user(self, user_id=0, convert_to_object=False):
        creature_data = self.QueryHandler.execute_query(TGOMMO_SELECT_USER_CREATURES_BY_USER_ID, params=(user_id,))

        if convert_to_object:
            creatures = []
            for creature in creature_data:
                creatures.append(
                    TGOCreature(
                        creature_id=creature[1],
                        catch_id=creature[0],

                        name=creature[2],
                        local_name=creature[3],
                        nickname=creature[4],
                        variant_name=creature[5],

                        dex_no=creature[6],
                        variant_no=creature[7],

                        full_name=creature[8],
                        scientific_name=creature[9],
                        kingdom=creature[10],
                        description=creature[11],

                        img_root=creature[12],
                        sub_environment=creature[13],
                        encounter_rate=creature[14],
                        rarity=get_rarity_by_name(creature[15]),

                        caught_date=creature[16],
                    )
                )
            return creatures
        return creature_data


    ''' Encyclopedia & Statistics Queries '''
    def get_total_user_catches_for_species(self, user_id=0, dex_no=0, variant_no=0):
        response = self.QueryHandler.execute_query(TGOMMO_GET_COUNT_FOR_USER_CATCHES_FOR_CREATURE_BY_DEX_NUM, params=(user_id, dex_no))
        return response[0][0]

    def user_has_caught_species(self, user_id=0, creature_id=0):
        response = self.QueryHandler.execute_query(TGOMMO_HAS_USER_CAUGHT_SPECIES, params=(user_id, creature_id))
        return response[0][0] == 0

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
    def get_encyclopedia_page_info(self, user_id=0, is_server_page=False, include_variants=False, include_mythics=False, environment:TGOEnvironment = None,  time_of_day=DAY):
        # GET TOTAL FOR CREATURES THAT CAN BE CAUGHT
        if include_variants:
            creature_count_query = TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_USER_BY_ID if not is_server_page else TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_SERVER_BY_ID
        else:
            creature_count_query = TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_USER_BY_DEX_NUM if not is_server_page else TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_SERVER_BY_DEX_NUM

        creature_count_params = (user_id, include_mythics) if not is_server_page else (include_mythics,)
        max_creatures_total = self.QueryHandler.execute_query(creature_count_query, params=creature_count_params)[0][0]

        # GET TOTAL FOR CREATURES CAUGHT
        # build query
        collected_creature_count_query = TGOMMO_GET_ENCYCLOPEDIA_PAGE_DISTINCT_CREATURE_CATCHES_FOR_USER_BASE if not is_server_page else TGOMMO_GET_ENCYCLOPEDIA_PAGE_DISTINCT_CREATURE_CATCHES_FOR_SERVER_BASE
        collected_creature_count_query += " AND e.variant_no=?" if time_of_day != BOTH else ""
        collected_creature_count_query += " AND c.variant_no = 1" if not include_variants else ""

        #build params
        collected_creature_count_params = (user_id, include_mythics, environment.dex_no) if not is_server_page else (include_mythics, environment.dex_no)
        if time_of_day != BOTH:
            collected_creature_count_params += (1 if time_of_day == DAY else 2,)

        caught_unique_creatures_total = self.QueryHandler.execute_query(f"{collected_creature_count_query};", params=collected_creature_count_params)[0][0]
        return (max_creatures_total, caught_unique_creatures_total)

    def get_ids_for_unique_creatures(self):
        response = self.QueryHandler.execute_query(TGOMMO_GET_IDS_FOR_UNIQUE_CREATURES, params=())
        return response[0]

    """ Player Profile Collection Queries """
    def get_active_collections(self, convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_GET_ALL_ACTIVE_COLLECTIONS, params=())

        if convert_to_object:
            collections = []
            for collection_data in response:
                collection = TGOCollection(collection_id=collection_data[0], title=collection_data[1], description=collection_data[2], image_path=collection_data[3], background_color_path=collection_data[4],  total_count_query=collection_data[5], caught_count_query=collection_data[6], completion_reward_1=collection_data[7], completion_reward_2=collection_data[8], completion_reward_3=collection_data[9], is_active=collection_data[10])
                collections.append(collection)
            return collections

        return response


    """ Player Avatar Unlock Queries """
    def get_users_who_played_during_time_range(self, min_timestamp='1900-01-01 00:00:00', max_timestamp='2100-01-01 00:00:00'):
        response = self.QueryHandler.execute_query(TGOMMO_GET_USERS_WHO_PLAYED_IN_TIMERANGE, params=(min_timestamp, max_timestamp))
        return response[0]

    def get_child_avatars_by_parent_id(self, parent_avatar_id='', convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_GET_ALL_CHILD_AVATARS_FOR_PARENT_AVATAR_ID, params=(parent_avatar_id, parent_avatar_id))

        if convert_to_object:
            avatars = []
            for avatar_details in response:
                avatar = TGOAvatar(avatar_num=avatar_details[0], avatar_id=avatar_details[1], name=avatar_details[2], avatar_type=avatar_details[3], img_root=avatar_details[4], series=avatar_details[5])
                avatars.append(avatar)
            return avatars
        return response


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
        response = self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_PROFILE_DISPLAY_CREATURES, params=params)
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
        self.QueryHandler.execute_query(TGOMMO_CREATE_AVATAR_TABLE)
        self.QueryHandler.execute_query(TGOMMO_CREATE_USER_AVATAR_LINK_TABLE)
        self.QueryHandler.execute_query(TGOMMO_CREATE_AVATAR_UNLOCK_CONDITION_TABLE)
        self.QueryHandler.execute_query(TGOMMO_CREATE_COLLECTION_TABLE)

        # Clear existing records
        self.QueryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_CREATURES, params=())
        self.QueryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_ENVIRONMENTS, params=())
        self.QueryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_ENVIRONMENT_CREATURES, params=())
        self.QueryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_AVATAR_UNLOCK_CONDITIONS, params=())
        self.QueryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_COLLECTIONS, params=())
        self.QueryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_USER_AVATAR, params=())
        # self.QueryHandler.execute_query(TGOMMO_DELETE_ALL_RECORDS_FROM_USER_PROFILE_AVATARS, params=())

        self.insert_creature_records()
        self.insert_transcendant_creature_records()
        self.insert_environment_records()
        self.insert_user_avatar_records()
        self.insert_user_avatar_unlock_condition_records()
        self.insert_collection_records()

        # Link creatures to environments
        self.insert_environment_creature_records()
        self.insert_transcendant_environment_creature_records()

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
        ]

        for index, creature in enumerate(creature_data):
            creature = (index + 1,) + creature
            self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_CREATURE, params=creature)

    def insert_transcendant_creature_records(self):
        transcendant_creature_data = [
            ('Bigfoot', '', BIGFOOT_DEX_NO, 1, 'Sasquatch', 'N/A', MYSTICAL, '', BIGFOOT_IMAGE_ROOT, 5, TGOMMO_RARITY_TRANSCENDANT),
            ('Mothman', '', MOTHMAN_DEX_NO, 1, 'Mothman', 'N/A', MYSTICAL, '', MOTHMAN_IMAGE_ROOT, 5, TGOMMO_RARITY_TRANSCENDANT),
            ('Frogman', '', FROGMAN_DEX_NO, 1, 'Loveland Frogman', 'N/A', MYSTICAL, '', FROGMAN_IMAGE_ROOT, 5, TGOMMO_RARITY_TRANSCENDANT),
            # ('Chupacabra', '', CHUPACABRA_DEX_NO, 1, 'Chupacabra', 'N/A', REPTILE, '', CHUPACABRA_IMAGE_ROOT, 5),
            # ('Jersey Devil', '', JERSEY_DEVIL_DEX_NO, 1, 'Jersey Devil', 'N/A', MAMMAL, '', JERSEY_DEVIL_IMAGE_ROOT, 5),
            # ('Thunderbird', '', THUNDERBIRD_DEX_NO, 1, 'Thunderbird', 'N/A', BIRD, '', THUNDERBIRD_IMAGE_ROOT, 5),
        ]

        for index, creature in enumerate(transcendant_creature_data):
            creature = (9000 + index + 1,) + creature
            self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_CREATURE, params=creature)

    def insert_environment_records(self):
        environment_data = [
            # 01 Eastern US Forest
            ('Eastern United States', 'Summer - Day', 1, 1, 'Eastern United States', '', 'est_us', False, True, 5),
            ('Eastern United States', 'Summer - Night',1, 2, 'Eastern United States', '', 'est_us', True, True, 5),
            ('Eastern United States', 'Winter - Day',1, 3, 'Eastern United States', '', 'est_us', False, False, 5),
            ('Eastern United States', 'Winter - Night', 1, 4, 'Eastern United States', '', 'est_us', False, False, 5),

            # 02 Everglades
            ('Everglades', 'Day', 2, 1, 'Florida', '', 'everglades', False, True, 5),
            ('Everglades', 'Night', 2, 2, 'Florida', '', 'everglades', True, True, 5),
        ]

        for index, environment in enumerate(environment_data):
            environment = (index + 1,) + environment
            self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_ENVIRONMENT, params=environment)

    def insert_environment_creature_records(self):
        environment_creature_data = [
            # Forest - Day Spawns
            self.format_creature_environment_link_params(DEER_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(DEER_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(GRAY_SQUIRREL_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(RABBIT_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(CHIPMUNK_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(ROBIN_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(SPARROW_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(SPARROW_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(BLUEJAY_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(GOLDFINCH_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(CARDINAL_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(CARDINAL_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(MONARCH_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(MONARCH_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(MONARCH_DEX_NO, 3, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(MANTIS_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(GARTERSNAKE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(BOXTURTLE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(TOAD_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(DUCK_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(DUCK_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(TURKEY_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(EAGLE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(BLACKBEAR_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(MOOSE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(MOOSE_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(CAT_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(CAT_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(CAT_DEX_NO, 3, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(CAT_DEX_NO, 4, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(GROUNDHOG_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(MOURNING_DOVE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(CANADA_GOOSE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(TURKEY_VULTURE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(CICADA_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(AMERICAN_CROW_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(RED_TAILED_HAWK_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(SNOWY_OWL_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(SKINK_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(RED_SQUIRREL_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(THIRTEEN_LINED_GROUND_SQUIRREL_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(HOUSE_FINCH_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(STARLING_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(BLACK_CAPPED_CHICKADEE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(BALTIMORE_ORIOLE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(REDWING_BLACKBIRD_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(REDWING_BLACKBIRD_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(PILEATED_WOODPECKER_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(HUMMINGBIRD_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(SNAIL_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(SNAIL_DEX_NO, 7, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(SWALLOWTAIL_BUTTERFLY_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(SWALLOWTAIL_BUTTERFLY_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(HONEYBEE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(LADYBUG_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(SPOTTED_LANTERNFLY_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(DRAGONFLY_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(POND_SKATER_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(BULL_FROG_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(PAINTED_TURTLE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(SEAGULL_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            self.format_creature_environment_link_params(CORMORANT_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_BEACH),
            self.format_creature_environment_link_params(KINGFISHER_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(MUTE_SWAN_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(GREAT_BLUE_HERON_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(SANDHILL_CRANE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(RIVER_OTTER_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(HERCULES_BEETLE_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(HERCULES_BEETLE_DEX_NO, 2, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(PUFFIN_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_BEACH),
            self.format_creature_environment_link_params(HARBOR_SEAL_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_BEACH),
            self.format_creature_environment_link_params(ALLIGATOR_DEX_NO, 1, EASTERN_US_FOREST_NO, 1, DAY,TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_RIVER),

            # Forest - Night Spawns
            self.format_creature_environment_link_params(DEER_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(DEER_DEX_NO, 2, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(RABBIT_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(RACCOON_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(MANTIS_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(GARTERSNAKE_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(TOAD_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(GREAT_HORNED_OWL_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(OPOSSUM_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(REDFOX_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(BOBCAT_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(BLACKBEAR_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(WOLF_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(CAT_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(CAT_DEX_NO, 2, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(CAT_DEX_NO, 3, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(CAT_DEX_NO, 4, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(MOUSE_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(SKUNK_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(CRICKET_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(FIREFLY_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(LUNA_MOTH_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(BLACK_WIDOW_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(SALAMANDER_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(SNAPPING_TURTLE_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(NIGHTHAWK_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(WOODCOCK_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(SCREECH_OWL_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(BAT_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(FLYING_SQUIRREL_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(PORCUPINE_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(COYOTE_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(MOUNTAIN_LION_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(COPPERHEAD_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(EARTHWORM_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(EASTERN_MOLE_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(STAR_NOSED_MOLE_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(STOAT_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(BOAR_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(BARN_SWALLOW_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(BARN_OWL_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(SNAIL_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(SNAIL_DEX_NO, 2, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(SNAIL_DEX_NO, 3, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(SNAIL_DEX_NO, 4, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(SNAIL_DEX_NO, 5, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(SNAIL_DEX_NO, 6, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(SNAIL_DEX_NO, 7, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_FIELD),
            self.format_creature_environment_link_params(TIGER_MOTH_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(POLYPHEMUS_MOTH_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(ROLYPOLY_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(SPOTTED_LANTERNFLY_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(NORTHERN_WALKING_STICK_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(BULL_FROG_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(BULL_FROG_DEX_NO, 2, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(EASTERN_NEWT_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(CRAYFISH_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_POND),
            self.format_creature_environment_link_params(KILLDEER_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_BEACH),
            self.format_creature_environment_link_params(LOON_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(BLACK_CROWNED_NIGHT_HERON_DEX_NO, 1, EASTERN_US_FOREST_NO, 2, NIGHT, TGOMMO_RARITY_RARE, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(MUSKRAT_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_COMMON, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(BEAVER_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_UNCOMMON, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(RIVER_OTTER_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_EPIC, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(HERCULES_BEETLE_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(HERCULES_BEETLE_DEX_NO, 2, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_GARDEN),
            self.format_creature_environment_link_params(HELLBENDER_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(ALLIGATOR_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_LEGENDARY, '', SUB_ENVIRONMENT_RIVER),
        ]

        for ec_link in environment_creature_data:
            self.QueryHandler.execute_query(TGOMMO_INSERT_ENVIRONMENT_CREATURE, params=ec_link)

    def insert_transcendant_environment_creature_records(self):
        environment_creature_data = [
            # EST US - Day Spawns
             self.format_creature_environment_link_params(BIGFOOT_DEX_NO, 1, EASTERN_US_FOREST_NO,  1, DAY, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(MOTHMAN_DEX_NO, 1, EASTERN_US_FOREST_NO,  1, DAY, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(FROGMAN_DEX_NO, 1, EASTERN_US_FOREST_NO,  1, DAY, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_RIVER),

            # EST US - Night Spawns
            self.format_creature_environment_link_params(BIGFOOT_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_FOREST),
            self.format_creature_environment_link_params(MOTHMAN_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_RIVER),
            self.format_creature_environment_link_params(FROGMAN_DEX_NO, 1, EASTERN_US_FOREST_NO,  2, NIGHT, TGOMMO_RARITY_TRANSCENDANT, '', SUB_ENVIRONMENT_RIVER),
        ]

        for ec_link in environment_creature_data:
            self.QueryHandler.execute_query(TGOMMO_INSERT_ENVIRONMENT_CREATURE, params=ec_link)

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
            self.QueryHandler.execute_query(TGOMMO_INSERT_COLLECTION, params=collection)

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

            # Event Avatars
            ('E1', 'Pim', AVATAR_TYPE_EVENT, 'Pim', 'Smiling Friends',),
            ('E2', 'Charlie', AVATAR_TYPE_EVENT, 'Charlie', 'Smiling Friends',),
            ('E3', 'Freddy Fazbear', AVATAR_TYPE_EVENT, 'Freddy', 'Smiling Friends',),
            ('E4', 'Allan', AVATAR_TYPE_EVENT, 'Allan', 'Smiling Friends',),
            ('E5', 'Glep', AVATAR_TYPE_EVENT, 'Glep', 'Smiling Friends',),
            ('E6', 'The Boss', AVATAR_TYPE_EVENT, 'TheBoss', 'Smiling Friends',),
            ('E7', 'Mr. Frog', AVATAR_TYPE_EVENT, 'MrFrog', 'Smiling Friends',),
            ('E8', 'Tyler', AVATAR_TYPE_EVENT, 'Tyler', 'Smiling Friends',),
            ('E9', 'Smormu', AVATAR_TYPE_EVENT, 'Smormu', 'Smiling Friends',),

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

            # Transcendant Avatars
            ('T1', 'Bigfoot', AVATAR_TYPE_TRANSCENDANT, 'Bigfoot', 'Cryptid',),
            ('T2', 'Mothman', AVATAR_TYPE_TRANSCENDANT, 'Mothman', 'Cryptid',),
            ('T3', 'Frogman', AVATAR_TYPE_TRANSCENDANT, 'Frogman', 'Cryptid',),

            # Fallback Avatars
            ('F1', 'Fallback-1', AVATAR_TYPE_FALLBACK, 'DefaultM', '',),
            ('F2', 'Fallback-2', AVATAR_TYPE_FALLBACK, 'DefaultF', '',),
        ]

        for index, avatar in enumerate(avatar_data):
            avatar = (index + 1,) + avatar
            if len(avatar) == 6:
                avatar = avatar + (False,)

            self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_USER_AVATAR, params=avatar)

            # for avatars unlocked server wide, insert a starter record into avatar link table
            if avatar[3] == AVATAR_TYPE_DEFAULT or avatar[3] == AVATAR_TYPE_SECRET:
                avatar_id = avatar[1]
                user_id = -1 if avatar[3] == AVATAR_TYPE_DEFAULT else 1
                self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_USER_AVATAR_LINK, params=(avatar_id, user_id))

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

            # Transcendant Avatars
            ('Bigfoot', ('T1', AVATAR_BIGFOOT_QUEST_QUERY,1, True)),
            ('Mothman', ('T2', AVATAR_MOTHMAN_QUEST_QUERY,1, True)),
            ('Frogman', ('T3', AVATAR_FROGMAN_QUEST_QUERY,1, True)),
        ]

        for index, avatar in enumerate(avatar_data):
            avatar_params = avatar[1]
            if len(avatar_params) == 3:
                avatar_params = avatar_params + (False,)

            self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_AVATAR_UNLOCK_CONDITION, params=avatar_params)


    def format_creature_environment_link_params(self, creature_dex_no, creature_variant_no, environment_dex_no, environment_variant_no, spawn_time, rarity, local_name='', sub_environment=SUB_ENVIRONMENT_FOREST):
        creature_info = self.get_creature_by_dex_and_variant_no(creature_dex_no, creature_variant_no)
        environment_info = self.get_environment_by_dex_and_variant_no(environment_dex_no, environment_variant_no)

        return (
            creature_info[0],
            environment_info[0],
            spawn_time,
            creature_info[1],
            environment_info[1],
            rarity,
            local_name,
            sub_environment
        )