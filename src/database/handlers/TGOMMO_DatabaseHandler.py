from src.database.handlers.EnvironmentCreatureLink import EnvironmentCreatureLink
from src.database.handlers.QueryHandler import QueryHandler
from src.discord.objects.CreatureRarity import *
from src.discord.objects.TGOAvatar import TGOAvatar
from src.discord.objects.TGOCollection import TGOCollection
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.discord.objects.TGOPlayer import TGOPlayer
from src.discord.objects.TGOPlayerItem import TGOPlayerItem
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.TGO_MMO_creature_constants import *
from src.resources.constants.queries.avatar_quest_db_queries import *
from src.resources.constants.general_constants import *
from src.resources.constants.queries.create_table_queries import *
from src.resources.constants.queries.db_queries import *


class TGOMMODatabaseHandler:
    def __init__(self, db_file):
        self.QueryHandler = QueryHandler(db_file=db_file)


    def execute_query(self, query, params=()):
        return self.QueryHandler.execute_query(query, params=params)


    '''**************'''
    ''' INSERT Queries '''
    '''**************'''
    ''' Creature Queries '''
    def insert_new_creature(self, params=(0,'', '', '', 0, 0, 0, 0, 0, 0, 0)):
        return self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_CREATURE, params=params)
    def insert_new_user_creature(self, params=(0,0,0,0,0)):
        return_value = self.QueryHandler.execute_query(TGOMMO_INSERT_USER_CREATURE, params=params)
        return return_value[0][0]

    ''' User Queries '''
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


    '''**************'''
    ''' SELECT Queries '''
    '''**************'''
    ''' Creature Queries'''
    # Creature Table Queries
    def get_creature_by_dex_and_variant_no(self, dex_no=0, variant_no=1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_CREATURE_BASE} {TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX} AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_VARIANT_NO_SUFFIX};"
        return self.get_creatures_from_database(query=query, params=(dex_no, variant_no), convert_to_object=convert_to_object, expect_multiple=False)

    # Environment Creature Table Queries
    def get_creatures_for_environment_by_environment_id(self, environment_id=-1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_CREATURE_BASE} {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_ID_SUFFIX} {TGOMMO_ORDER_BY_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX};"
        return self.get_environment_creatures_from_database(query=query, params=(environment_id, ), convert_to_object=convert_to_object, expect_multiple=True)

    def get_creatures_for_environment_by_dex_no(self, dex_no=0, convert_to_object=True):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_CREATURE_BASE} {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_DEX_NO_SUFFIX};"
        return self.get_environment_creatures_from_database(query=query, params=(dex_no,), convert_to_object=convert_to_object, expect_multiple=True)

    # User Creature Table Queries
    def get_user_creature_by_catch_id(self, catch_id=0, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_CREATURE_BASE} {TGOMMO_SELECT_USER_CREATURE_BY_CATCH_ID_SUFFIX};"
        return self.get_user_creatures_from_database(query=query, params=(catch_id,), convert_to_object=convert_to_object, expect_multiple=False)
    def get_user_creatures_by_user_id(self, user_id=0, is_released=False, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_CREATURE_BASE} {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX}"
        params = [user_id,]

        if is_released is not None:
            query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_IS_RELEASED_SUFFIX};"
            params.append(1 if is_released else 0)

        return self.get_user_creatures_from_database(query=query, params=params, convert_to_object=convert_to_object, expect_multiple=True)
    def get_released_user_creatures_by_user_id(self, user_id=-1, convert_to_object=False):
        query = f"{TGOMMO_SELECT_USER_CREATURE_BASE} {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX} AND {TGOMMO_SELECT_USER_CREATURE_BY_IS_RELEASED_SUFFIX};"
        return self.get_user_creatures_from_database(query=query, params=(user_id, 1), convert_to_object=convert_to_object, expect_multiple=True)

    # Encyclopedia Creature Queries
    def get_creatures_to_display_for_encyclopedia(self, environment_id=0, environment_variant_type=None, include_variants=False):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_CREATURE_BASE if environment_id != 0 else TGOMMO_SELECT_CREATURE_BASE}"
        params = []

        if environment_id != 0:
            query += " AND " if len(params) > 0 else ""

            query += f" {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_DEX_NO_SUFFIX}"
            params.append(environment_id)

            # add time of day filter if applicable
            if environment_variant_type != BOTH:
                query += f" AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_SPAWN_TIME_SUFFIX}"
                params.append(environment_variant_type)
        if not include_variants:
            query += " AND " if len(params) > 0 else ""
            query += f" {TGOMMO_SELECT_CREATURE_BY_CREATURE_VARIANT_NO_SUFFIX}"
            params.append(1)

        # add failsafe for cases where no creatures need to be excluded
        query += f"{TGOMMO_SELECT_CREATURE_PLACEHOLDER_SUFFIX} " if len(params) == 0 else ""
        # add ordering for environment or national dex
        query += f"{TGOMMO_ORDER_BY_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX if environment_id == 0 else TGOMMO_ORDER_BY_ENVIRONMENT_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX}"

        if environment_id == 0:
            encyclopedia_creatures = self.get_creatures_from_database(query=query, params=params, convert_to_object=True, expect_multiple=True)
        else:
            encyclopedia_creatures = self.get_environment_creatures_from_database(query=query, params=params, convert_to_object=True, expect_multiple=True)
        return encyclopedia_creatures

    def get_total_catches_for_creature_by_user(self, creature=None, user_id=0, environment_dex_no=None, environment_variant_type=None, group_variants=False,):
        query = f"{TGOMMO_SELECT_CREATURE_CAUGHT_TOTAL_BASE} AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX if group_variants else TGOMMO_SELECT_CREATURE_BY_CREATURE_ID_SUFFIX}"
        params = [creature.creature_id]

        if user_id is not None:
            query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX}"
            params.append(user_id)
        if not group_variants:
            query += f" AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_VARIANT_NO_SUFFIX}"
            params.append(creature.variant_no)

        if environment_dex_no is not None:
            query += f" AND {TGOMMO_SELECT_ENVIRONMENT_BY_DEX_NO_SUFFIX}"
            params.append(environment_dex_no)
            if environment_variant_type is not None:
                query += f" AND {TGOMMO_SELECT_ENVIRONMENT_BY_VARIANT_NO_SUFFIX}"
                params.append(environment_variant_type)

        response = self.QueryHandler.execute_query(query, params=tuple(params))
        return response[0]

    # Event Creature Queries
    def get_event_creatures_from_environment(self, convert_to_object=False):
        if not EVENT_SPAWN_POOL:
            return []

        # Create placeholders for each ID in the spawn pool
        event_creatures = []
        for event_pairing in EVENT_SPAWN_POOL:
            query = f"{TGOMMO_SELECT_ENVIRONMENT_CREATURE_BASE} {TGOMMO_SELECT_CREATURE_BY_CREATURE_ID_SUFFIX} AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_ID_SUFFIX};"
            event_creatures.append(self.get_creatures_from_database(query=query, params=(event_pairing[0], event_pairing[1]), convert_to_object=convert_to_object, expect_multiple=False))
        return event_creatures
    def get_environment_catch_stats_for_user(self, user_id=None, environment_dex_no=None):
        # grab actual user catches
        query = f"{TGOMMO_SELECT_USER_CATCHES_FOR_ENCYCLOPEDIA_BASE}"
        params = ()
        if user_id is not None:
            query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX}"
            params += (user_id, )
        if environment_dex_no is not None and environment_dex_no != 0:
            query += f" AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_DEX_NO_SUFFIX}"
            params += (environment_dex_no,)
        user_unique_catches = self.QueryHandler.execute_query(query, params=params)[0]

        # grab possible catches
        query = f"{TGOMMO_SELECT_POSSIBLE_CATCHES_FOR_ENCYCLOPEDIA_BASE}"
        params = ()
        if environment_dex_no is not None and environment_dex_no != 0:
            query += f" AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_DEX_NO_SUFFIX}"
            params = (environment_dex_no,)
        possible_unique_catches = self.QueryHandler.execute_query(query, params=params)[0]

        return user_unique_catches, possible_unique_catches

    # BASE FUNCTIONS FOR RETRIEVING CREATURES FROM THE DATABASE
    def get_creatures_from_database(self, query, params=(), convert_to_object=True, expect_multiple=False):
        results = self.QueryHandler.execute_query(query, params=params)

        creatures = results
        if convert_to_object:
            creatures = []
            for creature_details in results:
                creatures.append(
                    TGOCreature(
                        creature_id=creature_details[0],
                        name=creature_details[1], variant_name=creature_details[2],
                        dex_no=creature_details[3], variant_no=creature_details[4],
                        full_name=creature_details[5], scientific_name=creature_details[6], kingdom=creature_details[7],
                        description=creature_details[8],
                        img_root=creature_details[9],
                        encounter_rate=creature_details[10],
                        default_rarity=get_rarity_by_name(creature_details[11])
                    )
                )
        return creatures if expect_multiple else creatures[0]
    def get_environment_creatures_from_database(self, query, params=(), convert_to_object=True, expect_multiple=False):
        results = self.QueryHandler.execute_query(query, params=params)

        creatures = results
        if convert_to_object:
            creatures = []
            for creature_details in results:
                creatures.append(
                    TGOCreature(
                        creature_id=creature_details[0],
                        name=creature_details[1], variant_name=creature_details[2], local_name=creature_details[3],
                        dex_no=creature_details[4], variant_no=creature_details[5], local_dex_no=creature_details[6], local_variant_no=creature_details[7],
                        full_name=creature_details[8], scientific_name=creature_details[9], kingdom=creature_details[10], description=creature_details[11],
                        img_root=creature_details[12], local_image_root=creature_details[13],
                        sub_environment=creature_details[14],
                        encounter_rate=creature_details[15],
                        default_rarity=get_rarity_by_name(creature_details[16]), local_rarity=get_rarity_by_name(creature_details[17])
                    )
                )
        return creatures if expect_multiple else creatures[0]
    def get_user_creatures_from_database(self, query, params=(), convert_to_object=False, expect_multiple=False):
        results = self.QueryHandler.execute_query(query, params=params)

        creatures = results
        if convert_to_object:
            creatures = []
            for creature_details in results:
                creatures.append(
                    TGOCreature(
                        catch_id=creature_details[0], creature_id=creature_details[1],
                        name=creature_details[2], variant_name=creature_details[3], local_name=creature_details[4], nickname=creature_details[5],
                        dex_no=creature_details[6], variant_no=creature_details[7], local_dex_no=creature_details[8], local_variant_no=creature_details[9],
                        full_name=creature_details[10], scientific_name=creature_details[11], kingdom=creature_details[12], description=creature_details[13],
                        img_root=creature_details[14], local_image_root=creature_details[15],
                        sub_environment=creature_details[16],
                        encounter_rate=creature_details[17],
                        default_rarity=get_rarity_by_name(creature_details[18]), local_rarity=MYTHICAL if creature_details[20] else get_rarity_by_name(creature_details[19]),
                        caught_date=creature_details[21], is_favorite=bool(creature_details[22]),  is_released=bool(creature_details[23]),
                    )
                )
        return creatures if expect_multiple else creatures[0]


    ''' Environment Queries '''
    def get_environment_by_id(self, environment_id=-1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_BASE} {TGOMMO_SELECT_ENVIRONMENT_BY_ENVIRONMENT_ID_SUFFIX};"
        return self.get_environments_from_database(query=query, params=(environment_id,), convert_to_object=convert_to_object, expect_multiple=False)
    def get_environment_by_dex_no_and_variant_no(self, dex_no=0, variant_no=0, convert_to_object=True):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_BASE} {TGOMMO_SELECT_ENVIRONMENT_BY_DEX_NO_SUFFIX} AND {TGOMMO_SELECT_ENVIRONMENT_BY_VARIANT_NO_SUFFIX};"
        return self.get_environments_from_database(query=query, params=(dex_no, variant_no if variant_no != 0 else 1), convert_to_object=convert_to_object, expect_multiple=False)
    def get_environments_by_dex_no(self, dex_no=0, convert_to_object=True):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_BASE} {TGOMMO_SELECT_ENVIRONMENT_BY_DEX_NO_SUFFIX} {TGOMMO_ORDER_BY_ENVIRONMENT_DEX_NO_AND_VARIANT_NO_SUFFIX};"
        return self.get_environments_from_database(query=query, params=(dex_no, ), convert_to_object=convert_to_object, expect_multiple=True)

    def get_all_environments_in_rotation(self, is_day_night=1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_BASE} {TGOMMO_SELECT_ENVIRONMENT_BY_IN_CIRCULATION_SUFFIX} AND {TGOMMO_SELECT_ENVIRONMENT_BY_IS_NIGHT_ENVIRONMENT_SUFFIX} {TGOMMO_ORDER_BY_ENVIRONMENT_DEX_NO_AND_VARIANT_NO_SUFFIX};"
        return self.get_environments_from_database(query=query, params=(1, is_day_night), convert_to_object=convert_to_object, expect_multiple=True)
    def get_random_environment_in_rotation(self, is_night_environment= None, convert_to_object=False):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_BASE} {TGOMMO_SELECT_ENVIRONMENT_BY_IN_CIRCULATION_SUFFIX} AND {TGOMMO_SELECT_ENVIRONMENT_BY_IS_NIGHT_ENVIRONMENT_SUFFIX} {TGOMMO_ORDER_BY_RANDOM_SUFFIX};"
        return self.get_environments_from_database(query=query, params=(1, is_night_environment), convert_to_object=convert_to_object, expect_multiple=True)

    # BASE FUNCTIONS FOR RETRIEVING ENVIRONMENTS FROM THE DATABASE
    def get_environments_from_database(self, query, params=(), convert_to_object=False, expect_multiple=False):
        results = self.QueryHandler.execute_query(query, params=params)

        environments = results
        if convert_to_object:
            environments = []
            for env_details in results:
                environments.append(
                    TGOEnvironment(
                        environment_id=env_details[0],
                        name=env_details[1], variant_name=env_details[2],
                        dex_no=env_details[3], variant_no=env_details[4],
                        location=env_details[5], description=env_details[6],
                        img_root=env_details[7],
                        is_night_environment=bool(env_details[8]),
                        in_circulation=bool(env_details[9]),
                        encounter_rate=env_details[10]
                    )
                )

        return environments if expect_multiple else environments[0]


    ''' Player Profile Queries '''
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


    ''' Avatar Queries '''
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

    ''' Item Queries '''
    def get_user_item_by_user_id_and_item_id(self, user_id=0, item_id=0, convert_to_object=True):
        item_data = self.QueryHandler.execute_query(TGOMMO_SELECT_USER_ITEM_BY_USER_ID_AND_ITEM_ID, params=(user_id, item_id))[0]

        if convert_to_object:
            return TGOPlayerItem(
                item_id=item_data[1],
                item_num=item_data[0],

                item_name=item_data[2],
                 item_type=item_data[3],
                 item_description=item_data[4],

                rarity=get_rarity_by_name(item_data[5]),
                is_rewardable=item_data[6],
                img_root=item_data[7],
                default_uses=item_data[8],

                item_quantity=item_data[9],
                last_used=item_data[10],
            )
        return item_data
    def get_item_collection_by_user_id(self, user_id=0, convert_to_object=False):
        item_data = self.QueryHandler.execute_query(TGOMMO_SELECT_USER_ITEMS_BY_USER_ID, params=(user_id,))

        if convert_to_object:
            items = []
            for item in item_data:
                items.append(
                    TGOPlayerItem(
                        item_id=item[1],
                        item_num=item[0],

                        item_name=item[2],
                        item_type=item[3],
                        item_description=item[4],

                        rarity=get_rarity_by_name(item[5]),
                        is_rewardable=item[6],
                        img_root=item[7],
                        default_uses=item[8],

                        item_quantity=item[9],
                        last_used=item[10],
                    )
                )
            return items
        return item_data
    def get_inventory_item_by_item_id(self, item_id=-1, convert_to_object=False):
        item_details = self.QueryHandler.execute_query(TGOMMO_GET_INVENTORY_ITEM_BY_ITEM_ID, params=(item_id,))[0]

        if convert_to_object:
            return TGOPlayerItem(item_num=item_details[0], item_id=item_details[1], item_name=item_details[2], item_type=item_details[3], item_description=item_details[4], rarity=get_rarity_by_name(item_details[5]), is_rewardable=item_details[6], img_root=item_details[7], default_uses=item_details[8], )
        return item_details
    def get_rewardable_inventory_items(self, convert_to_object=False):
        response = self.QueryHandler.execute_query(TGOMMO_GET_ALL_REWARDABLE_INVENTORY_ITEMS, params=())

        if convert_to_object:
            items = []
            for item_details in response:
                rarity = get_rarity_by_name(item_details[5])
                item = TGOPlayerItem(item_num=item_details[0], item_id=item_details[1], item_name=item_details[2], item_type=item_details[3], item_description=item_details[4], rarity=rarity, is_rewardable=item_details[6], img_root=item_details[7], default_uses=item_details[8], )
                items.append(item)
            return items
        return response

    def get_creature_inventory_expansions_by_user_id(self, user_id=0):
        # Add Dummy Entry if User Doesn't Have Item Yet
        self.QueryHandler.execute_query(TGOMMO_INSERT_USER_ITEM_LINK, params=(ITEM_ID_CREATURE_INVENTORY_STORAGE_EXPANSION, user_id, 8, '1970-01-01 00:00:00'))
        return self.get_user_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_CREATURE_INVENTORY_STORAGE_EXPANSION).item_quantity


    ''' Encyclopedia & Statistics Queries '''
    # get total catches & mythicals for species
    def get_total_catches_for_species(self, creature=None, user_id=None, environment_dex_no=0, environment_variant_no=BOTH, group_variants=False, ):
        query = f"{TGOMMO_SELECT_CREATURE_CAUGHT_TOTAL_BASE} AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX if group_variants else TGOMMO_SELECT_CREATURE_BY_CREATURE_ID_SUFFIX}"
        params = [creature.dex_no if group_variants else creature.creature_id]

        if user_id is not None:
            query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX}"
            params.append(user_id)
        if not group_variants:
            query += f" AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_VARIANT_NO_SUFFIX}"
            params.append(creature.variant_no)

        if environment_dex_no != 0:
            query += f" AND {TGOMMO_SELECT_ENVIRONMENT_BY_DEX_NO_SUFFIX}"
            params.append(environment_dex_no)
            if environment_variant_no != BOTH:
                query += f" AND {TGOMMO_SELECT_ENVIRONMENT_BY_VARIANT_NO_SUFFIX}"
                params.append(1 if environment_variant_no == DAY else 2)

        response = self.QueryHandler.execute_query(query, params=tuple(params))
        return response[0]

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
    def get_user_catch_totals_for_environment(self, user_id=None, include_variants=False, include_mythics=False, environment:TGOEnvironment = None, time_of_day=None):
        query = f"{TGOMMO_SELECT_ALL_CREATURES_CAUGHT_TOTALS_BASE}"
        params = []

        if user_id:
            query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX}"
            params.append(user_id)
        # if not include_variants:
        #     query += f" AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_VARIANT_NO_SUFFIX}"
        #     params.append(1)
        if include_mythics:
            query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_IS_MYTHICAL_SUFFIX}"
            params.append(1)
        if environment.dex_no > 0:
            query += f" AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_DEX_NO_SUFFIX}"
            params.append(environment.dex_no)
        if time_of_day != BOTH:
            query += f" AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_SPAWN_TIME_SUFFIX}"
            params.append(time_of_day)

        results = self.QueryHandler.execute_query(query, params=tuple(params))[0]
        return results[0], results[2 if include_variants else 1]


    def get_first_caught_variant_for_creature(self, creature_dex_no, user_id= None, environment_dex_no= 0):
        query = f"{TGOMMO_SELECT_FIRST_CAUGHT_VARIANT_FOR_SPECIES_BASE}"
        params = [creature_dex_no]

        if user_id is not None:
            query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX}"
            params.append(user_id)
        if environment_dex_no != 0:
            query += f" AND {TGOMMO_SELECT_ENVIRONMENT_BY_DEX_NO_SUFFIX}"
            params.append(environment_dex_no)

        return self.QueryHandler.execute_query(query, params=params)[0][0]

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


    """ Avatar Unlock Queries """
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

    '''**************'''
    ''' UPDATE Queries '''
    '''**************'''
    # Creature Queries
    def update_creature_nickname(self, creature_id, nickname):
        response = self.QueryHandler.execute_query(TGOMMO_UPDATE_CREATURE_NICKNAME_BY_CATCH_ID, params=(nickname, creature_id))
        return response

    # Player Profile Queries
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

    def update_user_profile_currency(self, user_id, new_currency):
        user_currency = self.QueryHandler.execute_query(TGOMMO_USER_PROFILE_GET_CURRENCY_BY_USER_ID, params=(user_id,))[0][0]
        user_currency += new_currency

        response = self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_PROFILE_CURRENCY, params=(user_currency, user_id))
        return response
    def update_user_profile_available_items(self, user_id, item_id, new_amount):
        # add a dummy record in case user hasn't obtained this item before
        self.QueryHandler.execute_query(TGOMMO_INSERT_USER_ITEM_LINK, params=(item_id, user_id, 0, '1970-01-01 00:00:00'))
        response = self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_AVATAR_LINK_ITEM_COUNT, params=(new_amount, item_id, user_id))
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

    def update_user_creature_set_is_favorite(self, creature_ids, is_favorite=True):
        for creature_id in creature_ids:
            self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_CREATURE_IS_FAVORITE, params=(1 if is_favorite else 0, creature_id))
        return True
    def update_user_creature_set_is_released(self, creature_ids, is_released=True):
        # First check if any of the creatures are already released, if so don't release any creatures
        for creature_id in creature_ids:
            if self.QueryHandler.execute_query(TGOMMO_SELECT_USER_CREATURE_IS_RELEASED_BY_CREATURE_ID, params=(creature_id,))[0][0] == 1:
                return False

        # If none are released, proceed to release all creatures
        for creature_id in creature_ids:
                self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_CREATURE_IS_RELEASED, params=(1 if is_released else 0, creature_id))
        return True