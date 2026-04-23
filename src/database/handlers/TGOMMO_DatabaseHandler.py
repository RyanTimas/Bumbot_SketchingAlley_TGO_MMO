from src.commons.GuildHandler import get_guild
from src.database.handlers.QueryHandler import QueryHandler
from src.database.queries.tgommo_avatar_quest_db_queries import *
from src.database.queries.tgommo_db_queries import *
from src.discord.objects.CreatureRarity import *
from src.discord.objects.TGOAvatar import TGOAvatar
from src.discord.objects.TGOCollection import TGOCollection
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.discord.objects.TGOPlayer import TGOPlayer
from src.discord.objects.TGOPlayerItem import TGOPlayerItem
from src.resources.constants.TGO_MMO_constants import *


class TGOMMODatabaseHandler:
    def __init__(self, db_file):
        self.QueryHandler = QueryHandler(db_file=db_file)


    def execute_query(self, query, params=()):
        return self.QueryHandler.execute_query(query, params=params)


    """ ----- INSERT QUERIES  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
    # region INSERT QUERIES
    def insert_new_creature(self, params=(0,'', '', '', 0, 0, 0, 0, 0, 0, 0)):
        return self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_CREATURE, params=params)
    def insert_new_user_creature(self, params=(0,0,0,0,0)):
        return_value = self.QueryHandler.execute_query(TGOMMO_INSERT_USER_CREATURE, params=params)
        return return_value[0][0]

    def insert_new_user_profile(self, user_id=-1, nickname = ''):
        self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_USER_PROFILE, params=(user_id, nickname, 'D1', 1, -1, -1, -1, -1, -1, -1, 0, 3, 1, 0,  1, 0))
        return True

    def insert_new_user_profile_avatar_link(self, user_id=-1, avatar_id=-1):
        return self.QueryHandler.execute_query(TGOMMO_INSERT_NEW_USER_AVATAR_LINK, params=(avatar_id, user_id))
    def unlock_avatar_for_server(self, avatar_id=-1):
        return self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_AVATAR_UNLOCK_STATUS, params=(-1, avatar_id))
    def check_if_user_unlocked_avatar(self, user_id=-1, avatar_id=-1):
        return self.QueryHandler.execute_query(TGOMMO_AVATAR_IS_UNLOCKED_FOR_PLAYER, params=(user_id, avatar_id))[0][0] > 0

    def batch_insert_avatar_links(self, avatars, user_id):
        """Insert multiple avatar links at once"""
        values = [(avatar.avatar_id, user_id) for avatar in avatars]
        query = "INSERT INTO tgommo_user_profile_avatar_link (avatar_id, user_id) VALUES (?, ?)"
        self.QueryHandler.execute_many(query, values)
    # endregion


    '''' ----- SELECT QUERIES  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # region BASE QUERIES
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
                        full_name=creature_details[5], scientific_name=creature_details[6], kingdom=creature_details[7], description=creature_details[8],
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
                        environment_id=creature_details[18], sub_environment=creature_details[14],
                        full_name=creature_details[8], scientific_name=creature_details[9], kingdom=creature_details[10], description=creature_details[11],
                        img_root=creature_details[12], local_image_root=creature_details[13],
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
                        environment_id=creature_details[18], sub_environment=creature_details[16],
                        full_name=creature_details[10], scientific_name=creature_details[11], kingdom=creature_details[12], description=creature_details[13],
                        img_root=creature_details[14], local_image_root=creature_details[15],
                        encounter_rate=creature_details[17],
                        default_rarity=get_rarity_by_name(creature_details[18]), local_rarity=MYTHICAL if creature_details[20] else get_rarity_by_name(creature_details[19]),
                        caught_date=creature_details[21], is_favorite=bool(creature_details[22]),  is_released=bool(creature_details[23]),
                    )
                )
        return creatures if expect_multiple else creatures[0]

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
                        img_root=env_details[7], local_img_suffix=env_details[8],
                        is_night_environment=bool(env_details[9]), in_circulation=bool(env_details[10]), encounter_rate=env_details[11]
                    )
                )
        return environments if expect_multiple else environments[0]

    def get_player_profiles_from_database(self, query, params=(), convert_to_object=False, expect_multiple=False):
        results = self.QueryHandler.execute_query(query, params=params)

        user_profiles = results
        if convert_to_object:
            user_profiles = []
            for user_profile_details in results:
                user_profiles.append(
                    TGOPlayer(
                        player_id=user_profile_details[0], user_id=user_profile_details[1],
                        nickname=user_profile_details[2],
                        avatar=self.get_avatar_by_id(avatar_id=user_profile_details[3]), background_id=user_profile_details[4],
                        creature_slot_id_1=user_profile_details[5], creature_slot_id_2=user_profile_details[6], creature_slot_id_3=user_profile_details[7], creature_slot_id_4=user_profile_details[8], creature_slot_id_5=user_profile_details[9], creature_slot_id_6=user_profile_details[10],
                        currency=user_profile_details[11],
                        available_catch_attempts=user_profile_details[12],
                        rod_level=user_profile_details[13], rod_amount=user_profile_details[14], trap_level=user_profile_details[15], trap_amount=user_profile_details[16]
                    )
                )
        return user_profiles if expect_multiple else user_profiles[0]

    def get_avatars_from_database(self, query, params=(), convert_to_object=False, expect_multiple=False):
        results = self.QueryHandler.execute_query(query, params=params)
        if not results:
            return [] if expect_multiple else None

        avatars = results
        if convert_to_object:
            avatars = []
            for avatar_details in results:
                avatars.append(
                    TGOAvatar(
                        avatar_num=avatar_details[0], avatar_id=avatar_details[1],
                        name=avatar_details[2], avatar_type=avatar_details[3], series=avatar_details[4],
                        is_parent_entry=avatar_details[5],
                        img_root=avatar_details[6],
                        unlock_query=avatar_details[7], unlock_threshold=avatar_details[8], is_secret=avatar_details[9],
                        shop_price=avatar_details[10],
                        unlock_startdate=avatar_details[11], unlock_enddate=avatar_details[12]
                    )
                )
        return avatars if expect_multiple else avatars[0]
    def get_inventory_items_from_database(self, query, params=(), convert_to_object=False, expect_multiple=False):
        results = self.QueryHandler.execute_query(query, params=params)

        inventory_items = results
        if convert_to_object:
            inventory_items = []
            for inventory_item_details in results:
                inventory_items.append(
                    TGOPlayerItem(
                        item_num=inventory_item_details[0], item_id=inventory_item_details[1],
                        item_name=inventory_item_details[2], item_type=inventory_item_details[3], item_description=inventory_item_details[4],
                        rarity=get_rarity_by_name(inventory_item_details[5]), is_rewardable=inventory_item_details[6], img_root=inventory_item_details[7], default_uses=inventory_item_details[8],
                        user_id=inventory_item_details[9], item_quantity=inventory_item_details[10], last_used=inventory_item_details[11],
                        last_purchase_date=inventory_item_details[12], shop_price=inventory_item_details[13]
                    )
                )
        return inventory_items if expect_multiple else inventory_items[0]

    def get_collections_from_database(self, query, params=(), convert_to_object=False, expect_multiple=False):
        results = self.QueryHandler.execute_query(query, params=params)

        collections = results
        if convert_to_object:
            collections = []
            for collection_details in results:
                collections.append(
                    TGOCollection(
                        collection_id=collection_details[0],
                        title=collection_details[1], description=collection_details[2],
                        image_path=collection_details[3], background_color_path=collection_details[4],
                        total_count_query=collection_details[5], caught_count_query=collection_details[6],
                        completion_reward_1=collection_details[7], completion_reward_2=collection_details[8], completion_reward_3=collection_details[9],
                        is_active=bool(collection_details[10])
                    )
                )
        return collections if expect_multiple else collections[0]
    # endregion

    # region CREATURE QUERIES
    # region select creature queries
    def get_all_creatures(self, convert_to_object=True):
        query = f"{TGOMMO_SELECT_CREATURE_BASE} TRUE {TGOMMO_ORDER_BY_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX};"
        return self.get_creatures_from_database(query=query, params=(), convert_to_object=convert_to_object, expect_multiple=True)
    def get_creature_by_creature_id(self, creature_id=-1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_CREATURE_BASE} {TGOMMO_SELECT_CREATURE_BY_CREATURE_ID_SUFFIX};"
        return self.get_creatures_from_database(query=query, params=(creature_id,), convert_to_object=convert_to_object, expect_multiple=False)
    def get_creature_by_dex_and_variant_no(self, dex_no=0, variant_no=1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_CREATURE_BASE} {TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX} AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_VARIANT_NO_SUFFIX};"
        return self.get_creatures_from_database(query=query, params=(dex_no, variant_no), convert_to_object=convert_to_object, expect_multiple=False)

    def get_all_environment_creatures(self, convert_to_object=True):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_CREATURE_BASE} TRUE {TGOMMO_ORDER_BY_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX};"
        return self.get_environment_creatures_from_database(query=query, params=(), convert_to_object=convert_to_object, expect_multiple=True)
    def get_environment_creature_by_environment_id_and_creature_id(self, environment_id=-1, creature_id=-1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_CREATURE_BASE} {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_ID_SUFFIX} AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_ID_SUFFIX};"
        return self.get_environment_creatures_from_database(query=query, params=(environment_id, creature_id), convert_to_object=convert_to_object, expect_multiple=False)
    def get_creatures_for_environment_by_environment_id(self, environment_id=-1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_CREATURE_BASE} {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_ID_SUFFIX} {TGOMMO_ORDER_BY_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX};"
        return self.get_environment_creatures_from_database(query=query, params=(environment_id, ), convert_to_object=convert_to_object, expect_multiple=True)
    def get_creatures_for_environment_by_dex_no(self, dex_no=0, convert_to_object=True):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_CREATURE_BASE} {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_DEX_NO_SUFFIX};"
        return self.get_environment_creatures_from_database(query=query, params=(dex_no,), convert_to_object=convert_to_object, expect_multiple=True)

    def get_user_creature_by_catch_id(self, catch_id=0, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_CREATURE_BASE} {TGOMMO_SELECT_USER_CREATURE_BY_CATCH_ID_SUFFIX};"
        return self.get_user_creatures_from_database(query=query, params=(catch_id,), convert_to_object=convert_to_object, expect_multiple=False)
    def get_user_creatures_by_catch_ids(self, catch_ids, convert_to_object=True):
        placeholders = ','.join(['?' for _ in catch_ids])
        query = f"{TGOMMO_SELECT_USER_CREATURE_BASE} {TGOMMO_CATCH_ID_IN_SUFFIX} ({placeholders});"
        return self.get_user_creatures_from_database(query=query, params=catch_ids, convert_to_object=convert_to_object, expect_multiple=True)

    def get_user_creatures_by_user_id(self, user_id=0, is_released=False, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_CREATURE_BASE} {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX}"
        params = [user_id,]

        if is_released is not None:
            query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_IS_RELEASED_SUFFIX};"
            params.append(1 if is_released else 0)

        return self.get_user_creatures_from_database(query=query, params=params, convert_to_object=convert_to_object, expect_multiple=True)
    def get_user_creatures_by_user_id_and_dex_no(self, user_id=0, dex_no=0, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_CREATURE_BASE} {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX} AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX};"
        return self.get_user_creatures_from_database(query=query, params=(user_id, dex_no,),convert_to_object=convert_to_object, expect_multiple=True)
    def get_user_creatures_by_user_id_and_dex_no_and_variant_no(self, user_id=0, dex_no=0, variant_no=0, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_CREATURE_BASE} {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX} AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX} AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_VARIANT_NO_SUFFIX};"
        return self.get_user_creatures_from_database(query=query, params=(user_id, dex_no, variant_no), convert_to_object=convert_to_object, expect_multiple=True)
    def get_mythical_user_creatures_by_user_id_and_dex_no(self, user_id=0, dex_no=0, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_CREATURE_BASE} {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX} AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX} AND {TGOMMO_SELECT_USER_CREATURE_BY_IS_MYTHICAL_SUFFIX};"
        return self.get_user_creatures_from_database(query=query, params=(user_id, dex_no), convert_to_object=convert_to_object, expect_multiple=True)
    def get_mythical_user_creatures_by_user_id_and_dex_no_and_variant_no(self, user_id=0, dex_no=0, variant_no=1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_CREATURE_BASE} {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX} AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX} AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_VARIANT_NO_SUFFIX} AND {TGOMMO_SELECT_USER_CREATURE_BY_IS_MYTHICAL_SUFFIX};"
        return self.get_user_creatures_from_database(query=query, params=(user_id, dex_no, variant_no), convert_to_object=convert_to_object, expect_multiple=True)
    # endregion

    # region CATCH STAT QUERIES
    # region CATCH STAT QUERIES - total catches
    def get_total_catches_base(self, user_id=None, include_variants=False, creature_dex_no=None, creature_id=None, environment_dex_no=None, time_of_day=None, is_mythical=False, rarity=None, creature_class=None, is_released=None):
        query = f"{TGOMMO_SELECT_TOTAL_CREATURES_CAUGHT_BASE} true "
        query, params = self.handle_user_creature_optional_query_extensions(base_query=query, params=[], user_id=user_id, creature_id=creature_id, creature_dex_no=creature_dex_no, environment_dex_no=environment_dex_no, environment_variant_no=time_of_day, is_mythical=is_mythical, rarity=rarity, creature_class=creature_class, is_released=is_released)

        return self.QueryHandler.execute_query(query, params=params)[0][0]

    def has_user_caught_creature(self, user_id=0, dex_no=0):
        return self.get_total_catches_for_creature_by_user(user_id=user_id, dex_no=dex_no) > 0
    def has_user_caught_mythical_creature(self, user_id=0, dex_no=0):
        return self.get_total_mythical_catches_for_creature_by_user(user_id=user_id, dex_no=dex_no) > 0
    def has_user_caught_creature_variant(self, user_id=0, creature_id=0):
        return self.get_total_catches_for_creature_variant_by_user(user_id=user_id, creature_id=creature_id) > 0
    def has_user_caught_mythical_creature_variant(self, user_id=0, creature_id=0):
        return self.get_total_mythical_catches_for_creature_variant_by_user(user_id=user_id, creature_id=creature_id) > 0

    def does_user_own_catch_id(self, user_id=0, catch_id=0):
        query = f"{TGOMMO_SELECT_USER_CREATURE_BASE} {TGOMMO_SELECT_USER_CREATURE_BY_CATCH_ID_SUFFIX} AND {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX};"
        return self.QueryHandler.execute_query(query, params=(catch_id, user_id)) != []

    def get_total_catches_for_user(self, user_id=0, is_released=None):
        return self.get_total_catches_base(user_id=user_id, is_released=is_released)
    def get_total_mythical_catches_for_user(self, user_id=0, is_released=None):
        return self.get_total_catches_base(user_id=user_id, is_mythical=True, is_released=is_released)
    def get_total_catches_for_server(self, is_released=None):
        return self.get_total_catches_base(is_released=is_released)
    def get_total_mythical_catches_for_server(self, is_released=None):
        return self.get_total_catches_base(is_mythical=True, is_released=None)

    def get_total_catches_for_species_for_environment(self, user_id=0, creature_dex_no=0, creature_id=0, environment_dex_no=0, time_of_day=BOTH, is_mythical=False):
        query = f"{TGOMMO_SELECT_TOTAL_CREATURES_CAUGHT_BASE} true "
        params = []
        if environment_dex_no != 0:
            query += f" AND {TGOMMO_SELECT_ENVIRONMENT_BY_DEX_NO_SUFFIX}"
            params.append(environment_dex_no)
        query, additional_params = self.handle_user_creature_optional_query_extensions(base_query=query, params=[], user_id=user_id, creature_dex_no=creature_dex_no, creature_id=creature_id, environment_variant_no=time_of_day, is_mythical=is_mythical)
        params = params + additional_params

        return self.QueryHandler.execute_query(query, params=params)[0][0]


    def get_total_catches_for_creature_by_user(self, user_id=0, dex_no=0):
        return self.get_total_catches_base(user_id=user_id, include_variants=False, creature_dex_no=dex_no)
    def get_total_catches_for_creature_variant_by_user(self, user_id=0, creature_id=0):
        return self.get_total_catches_base(user_id=user_id, include_variants=True, creature_id=creature_id)
    def get_total_mythical_catches_for_creature_by_user(self, user_id=0, dex_no=0):
        return self.get_total_catches_base(user_id=user_id, include_variants=False, creature_dex_no=dex_no, is_mythical=True)
    def get_total_mythical_catches_for_creature_variant_by_user(self, user_id=0, creature_id=0):
        return self.get_total_catches_base(user_id=user_id, include_variants=True, creature_id=creature_id, is_mythical=True)
    # endregion

    # region CATCH STAT QUERIES - unique catches
    def get_unique_catches_base(self, user_id=None, include_variants=False, creature_dex_no=None, creature_id=None, environment_dex_no= None,  environment_id= None, time_of_day=None, rarity=None, creature_class=None, is_mythical=False):
        query = f"{TGOMMO_SELECT_UNIQUE_CREATURE_VARIANTS_CAUGHT_BASE if include_variants else TGOMMO_SELECT_UNIQUE_CREATURES_CAUGHT_BASE} true "
        query, params = self.handle_user_creature_optional_query_extensions(base_query=query, params=[], user_id=user_id, creature_id=creature_id, creature_dex_no=creature_dex_no, environment_dex_no=environment_dex_no, environment_variant_no=time_of_day, is_mythical=is_mythical, rarity=rarity, creature_class=creature_class)

        return self.QueryHandler.execute_query(query, params=params)[0][0]

    def get_total_unique_creatures_caught_by_user(self, user_id=0):
        return self.get_unique_catches_base(user_id=user_id, include_variants=False)
    def get_total_unique_creature_variants_caught_by_user(self, user_id=0):
        return self.get_unique_catches_base(user_id=user_id, include_variants=True)
    def get_total_unique_mythical_creatures_caught_by_user(self, user_id=0):
        return self.get_unique_catches_base(user_id=user_id, include_variants=False, is_mythical=True)
    def get_total_unique_mythical_creature_variants_caught_by_user(self, user_id=0):
        return self.get_unique_catches_base(user_id=user_id, include_variants=True, is_mythical=True)

    def get_total_unique_creature_variants_caught_in_environment(self, environment_dex_no=0):
        query = f"{TGOMMO_SELECT_UNIQUE_CREATURE_VARIANTS_CAUGHT_BASE} {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_DEX_NO_SUFFIX} AND {TGOMMO_SELECT_USER_CREATURE_BY_MATCHES_ENVIRONMENT_SUFFIX}"
        return self.QueryHandler.execute_query(query, params=(environment_dex_no,))[0][0]

    def get_total_unique_creatures_caught_by_user_and_environment_dex_no(self, user_id=0, environment_dex_no=0):
        return self.get_unique_catches_base(user_id=user_id, include_variants=False, environment_dex_no=environment_dex_no)
    def get_total_unique_creature_variants_caught_by_user_and_environment_dex_no(self, user_id=0, environment_dex_no=0):
        return self.get_unique_catches_base(user_id=user_id, include_variants=True, environment_dex_no=environment_dex_no)
    def get_total_unique_mythical_creatures_caught_by_user_and_environment_dex_no(self, user_id=0, environment_dex_no=0):
        return self.get_unique_catches_base(user_id=user_id, include_variants=False, environment_dex_no=environment_dex_no, is_mythical=True)
    def get_total_unique_mythical_creature_variants_caught_by_user_and_environment_dex_no(self, user_id=0, environment_dex_no=0):
        return self.get_unique_catches_base(user_id=user_id, include_variants=True, environment_dex_no=environment_dex_no, is_mythical=True)
    # endregion

    # region CATCH STAT QUERIES # region CATCH STAT QUERIES - unique catches
    def get_total_unique_creatures_available_base(self, user_id=None, include_variants=False, include_mythics=False, environment_dex_no= None, environment_id=None, time_of_day=None, rarity=None, creature_class=None):
        query = f"{TGOMMO_SELECT_TOTAL_UNIQUE_VARIANTS_AVAILABLE_BASE if include_variants else TGOMMO_SELECT_TOTAL_UNIQUE_CREATURES_AVAILABLE_BASE} {TGOMMO_SELECT_CREATURE_BY_EXCLUDING_TRANSCENDANT_DEFAULT_RARITY_SUFFIX} "
        query, params = self.handle_user_creature_optional_query_extensions(base_query=query, params=[], user_id=user_id, environment_dex_no=environment_dex_no, environment_variant_no=time_of_day, is_mythical=include_mythics, rarity=rarity, creature_class=creature_class)

        return self.QueryHandler.execute_query(query, params=params)[0][0]

    def get_total_unique_creatures_available_for_environment(self, environment_dex_no=None, include_variants=False, time_of_day=None, rarity=None, creature_class=None):
        return self.get_total_unique_creatures_available_base(environment_dex_no=environment_dex_no, include_variants=include_variants, time_of_day=time_of_day, rarity=rarity, creature_class=creature_class)
    # endregion
    # endregion

    # region MISC CREATURE QUERIES
    def get_event_creatures_from_environment(self, convert_to_object=False):
        if not EVENT_SPAWN_POOL:
            return []

        # Create placeholders for each ID in the spawn pool
        event_creatures = []
        for event_pairing in EVENT_SPAWN_POOL:
            query = f"{TGOMMO_SELECT_ENVIRONMENT_CREATURE_BASE} {TGOMMO_SELECT_CREATURE_BY_CREATURE_ID_SUFFIX} AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_ID_SUFFIX};"
            event_creatures.append(self.get_creatures_from_database(query=query, params=(event_pairing[0], event_pairing[1]), convert_to_object=convert_to_object, expect_multiple=False))
        return event_creatures
    def get_creatures_to_display_for_encyclopedia(self, environment_id=0, environment_variant_type=None, include_variants=False, rarity=None, creature_class=None):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_CREATURE_BASE if environment_id != 0 else TGOMMO_SELECT_CREATURE_BASE} TRUE "
        params = []

        if environment_id != 0:
            query += f" AND  {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_DEX_NO_SUFFIX}"
            params.append(environment_id)

            # add time of day filter if applicable
            if environment_variant_type != BOTH:
                query += f" AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_SPAWN_TIME_SUFFIX}"
                params.append(environment_variant_type)
            if rarity:
                query += f" AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_RARITY_SUFFIX}"
                params.append(rarity)

        if creature_class:
            query += f" AND {TGOMMO_SELECT_CREATURE_BY_CLASSIFICATION_SUFFIX}"
            params.append(creature_class)

        if not include_variants:
            query += f" AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_VARIANT_NO_SUFFIX}"
            params.append(1)

        # add group by clause for getting a single instance for "both" time spawns
        query += f" {TGOMMO_GROUP_BY_CREATURE_BY_CREATURE_ID_SUFFIX }"
        # add ordering for environment or national dex
        query += f"{TGOMMO_ORDER_BY_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX if environment_id == 0 else TGOMMO_ORDER_BY_ENVIRONMENT_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX}"

        if environment_id == 0:
            encyclopedia_creatures = self.get_creatures_from_database(query=query, params=params, convert_to_object=True, expect_multiple=True)
        else:
            encyclopedia_creatures = self.get_environment_creatures_from_database(query=query, params=params, convert_to_object=True, expect_multiple=True)
        return encyclopedia_creatures
    def get_environment_catch_stats_for_user(self, user_id=None, environment_dex_no=None):
        user_unique_creature_catches = self.get_total_unique_creatures_caught_by_user(user_id=user_id) if environment_dex_no is None else self.get_total_unique_creatures_caught_by_user_and_environment_dex_no(user_id=user_id, environment_dex_no=environment_dex_no)
        user_unique_creature_variant_catches = self.get_total_unique_creature_variants_caught_by_user(user_id=user_id) if environment_dex_no is None else self.get_total_unique_creature_variants_caught_by_user_and_environment_dex_no(user_id=user_id, environment_dex_no=environment_dex_no)
        user_unique_mythical_creature_catches = self.get_total_unique_mythical_creatures_caught_by_user(user_id=user_id) if environment_dex_no is None else self.get_total_unique_mythical_creatures_caught_by_user_and_environment_dex_no(user_id=user_id, environment_dex_no=environment_dex_no)

        possible_unique_creature_catches = self.get_total_unique_creatures_available_for_environment(environment_dex_no=environment_dex_no)
        possible_unique_creature_variants_catches = self.get_total_unique_creatures_available_for_environment(environment_dex_no=environment_dex_no, include_variants=True)
        possible_unique_mythical_creature_catches = possible_unique_creature_catches

        user_unique_catches = [user_unique_creature_catches, user_unique_creature_variant_catches, user_unique_mythical_creature_catches]
        possible_unique_catches = [possible_unique_creature_catches, possible_unique_creature_variants_catches, possible_unique_mythical_creature_catches]

        return user_unique_catches, possible_unique_catches
    def get_first_caught_variant_for_creature(self, creature_dex_no, user_id= None, environment_dex_no= 0, is_mythical=False):
        query = f"{TGOMMO_SELECT_FIRST_CAUGHT_VARIANT_FOR_SPECIES_BASE} {TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX}"
        params = [creature_dex_no]

        if user_id != 0:
            query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX}"
            params.append(user_id)
        if environment_dex_no != 0:
            query += f" AND {TGOMMO_SELECT_ENVIRONMENT_BY_DEX_NO_SUFFIX}"
            params.append(environment_dex_no)
        if is_mythical:
            query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_IS_MYTHICAL_SUFFIX}"
            params.append(1)

        return self.QueryHandler.execute_query(query, params=params)[0][0]
    # endregion
    # endregion

    # region ENVIRONMENT QUERIES
    # region SELECT ENVIRONMENT QUERIES
    def get_environment_by_id(self, environment_id=-1, convert_to_object=True):
        query, params = self.handle_environment_optional_query_extensions(base_query=f"{TGOMMO_SELECT_ENVIRONMENT_BASE} true ", params=[], environment_id=environment_id)
        return self.get_environments_from_database(query=query, params=(environment_id,), convert_to_object=convert_to_object, expect_multiple=False)
    def get_environments_by_dex_no(self, dex_no=0, convert_to_object=True):
        query, params = self.handle_environment_optional_query_extensions(base_query=f"{TGOMMO_SELECT_ENVIRONMENT_BASE} true ", params=[], environment_dex_no=dex_no)
        return self.get_environments_from_database(query=query, params=(dex_no, ), convert_to_object=convert_to_object, expect_multiple=True)
    def get_environment_by_dex_no_and_variant_no(self, dex_no=0, variant_no=0, convert_to_object=True):
        query, params = self.handle_environment_optional_query_extensions(base_query=f"{TGOMMO_SELECT_ENVIRONMENT_BASE} true ", params=[], environment_dex_no=dex_no, variant_no=variant_no)
        return self.get_environments_from_database(query=query, params=(dex_no, variant_no if variant_no != 0 else 1), convert_to_object=convert_to_object, expect_multiple=False)
    # endregion

    # region MISC ENVIRONMENT QUERIES
    def get_all_environments_in_rotation(self, is_day_night=1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_BASE} {TGOMMO_SELECT_ENVIRONMENT_BY_IN_CIRCULATION_SUFFIX} AND {TGOMMO_SELECT_ENVIRONMENT_BY_IS_NIGHT_ENVIRONMENT_SUFFIX} {TGOMMO_ORDER_BY_ENVIRONMENT_DEX_NO_AND_VARIANT_NO_SUFFIX};"
        return self.get_environments_from_database(query=query, params=(1, is_day_night), convert_to_object=convert_to_object, expect_multiple=True)
    def get_random_environment_in_rotation(self, is_night_environment= None, convert_to_object=False):
        query = f"{TGOMMO_SELECT_ENVIRONMENT_BASE} {TGOMMO_SELECT_ENVIRONMENT_BY_IN_CIRCULATION_SUFFIX} AND {TGOMMO_SELECT_ENVIRONMENT_BY_IS_NIGHT_ENVIRONMENT_SUFFIX} {TGOMMO_ORDER_BY_RANDOM_SUFFIX};"
        return self.get_environments_from_database(query=query, params=(1, is_night_environment, 1), convert_to_object=convert_to_object, expect_multiple=False)
    # endregion
    # endregion

    # region PLAYER PROFILE QUERIES
    def get_user_profile_by_user_id(self, user_id=0, convert_to_object=True):
        player_discord_profile = get_guild().get_member(user_id)
        self.insert_new_user_profile(user_id=user_id, nickname="User" if not player_discord_profile else player_discord_profile.display_name)

        query = f"{TGOMMO_SELECT_USER_PROFILE_BASE} {TGOMMO_SELECT_USER_PROFILE_BY_USER_ID_SUFFIX};"
        return self.get_player_profiles_from_database(query=query, params=(user_id,), convert_to_object=convert_to_object, expect_multiple=False)

    def get_players_who_played_during_time_range(self, min_timestamp='1900-01-01 00:00:00', max_timestamp='2100-01-01 00:00:00'):
        user_ids = self.QueryHandler.execute_query(TGOMMO_GET_USERS_WHO_PLAYED_IN_TIMERANGE, params=(min_timestamp, max_timestamp))[0]

        users = []
        for user_id in user_ids:
            query = f"{TGOMMO_SELECT_USER_PROFILE_BASE} {TGOMMO_SELECT_USER_AVATAR_BY_AVATAR_ID_SUFFIX};"
            users.append(self.get_player_profiles_from_database(query=query, params=(user_id,), convert_to_object=True, expect_multiple=False))
        return users
    # endregion

    # region AVATAR QUERIES
    def get_avatar_by_id(self, avatar_id, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_AVATAR_BASE} {TGOMMO_SELECT_USER_AVATAR_LINK_BY_AVATAR_ID_SUFFIX};"
        return self.get_avatars_from_database(query=query, params=(avatar_id,), convert_to_object=convert_to_object, expect_multiple=False)

    def get_unlocked_avatars_by_user_id(self, user_id, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_AVATAR_BASE} {TGOMMO_SELECT_USER_AVATAR_LINK_BY_USER_ID_SUFFIX};"
        return self.get_avatars_from_database(query=query, params=(user_id,), convert_to_object=convert_to_object, expect_multiple=True)
    def get_unlocked_avatars_for_server(self, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_AVATAR_BASE} {TGOMMO_SELECT_USER_AVATAR_LINK_BY_USER_ID_SUFFIX};"
        return self.get_avatars_from_database(query=query, params=(-1,), convert_to_object=convert_to_object, expect_multiple=True)
    def has_user_unlocked_avatar(self, user_id=0, avatar_id=0):
        query = f"{TGOMMO_SELECT_USER_AVATAR_BASE} {TGOMMO_SELECT_USER_AVATAR_LINK_BY_USER_ID_SUFFIX} AND {TGOMMO_SELECT_USER_AVATAR_LINK_BY_AVATAR_ID_SUFFIX};"
        result = self.get_avatars_from_database(query=query, params=(user_id, avatar_id), convert_to_object=False, expect_multiple=False)
        return True if result else False

    # QUEST AVATAR QUERIES
    def get_avatars_with_unlock_conditions(self, exclude_unlocked_avatars=False, user_id=1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_AVATAR_BASE} {TGOMMO_SELECT_USER_AVATAR_UNLOCK_CONDITION_BY_UNLOCK_QUERY_NOT_NULL_SUFFIX}"
        params = ()

        if exclude_unlocked_avatars:
            query += f" AND {TGOMMO_NOT_EXISTS_USER_AVATAR_ID_IN_USER_PROFILE_AVATAR_LINK_SUFFIX}"
            params += (user_id,)
        query += f" {TGOMMO_SELECT_USER_AVATAR_GROUP_BY_DISTINCT_AVATAR_SUFFIX};"

        return self.get_avatars_from_database(query=query, params=params, convert_to_object=convert_to_object, expect_multiple=True)
    def get_child_avatars_by_parent_id(self, parent_avatar_id=''):
        query = f"{TGOMMO_SELECT_USER_AVATAR_BASE} {TGOMMO_SELECT_USER_AVATAR_BY_CHILD_AVATAR_SUFFIX};"
        return self.get_avatars_from_database(query=query, params=(parent_avatar_id, parent_avatar_id), convert_to_object=True, expect_multiple=True)

    def batch_check_unlocked_avatars(self, avatar_ids, user_id):
        """Returns set of avatar_ids that are already unlocked"""
        placeholders = ','.join(['?' for _ in avatar_ids])
        query = f"""SELECT avatar_id FROM tgommo_user_profile_avatar_link WHERE avatar_id IN ({placeholders}) AND user_id = ?"""
        results = self.QueryHandler.execute_query(query, avatar_ids + [user_id])
        return {row[0] for row in results}

    # EVENT AVATAR QUERIES
    def get_all_limited_time_avatars(self, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_AVATAR_BASE} {TGOMMO_SELECT_USER_AVATAR_BY_NON_NULL_START_DATE_SUFFIX};"
        return self.get_avatars_from_database(query=query, params=(), convert_to_object=convert_to_object, expect_multiple=True)
    def get_currently_available_limited_time_avatars(self, exclude_unlocked_avatars=False, user_id=1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_AVATAR_BASE} {TGOMMO_SELECT_USER_AVATAR_BY_DATE_BETWEEN_START_AND_END_DATE_SUFFIX} "
        params = ()

        if exclude_unlocked_avatars:
            query += f" AND {TGOMMO_NOT_EXISTS_USER_AVATAR_ID_IN_USER_PROFILE_AVATAR_LINK_SUFFIX}"
            params += (user_id,)
        query += f" {TGOMMO_SELECT_USER_AVATAR_GROUP_BY_DISTINCT_AVATAR_SUFFIX};"

        return self.get_avatars_from_database(query=query, params=params, convert_to_object=convert_to_object, expect_multiple=True)

    # SECRET AVATAR QUERIES
    def get_avatars_by_nickname(self, nickname='', exclude_unlocked_avatars=False, user_id=1, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_AVATAR_BASE} {TGOMMO_SELECT_USER_AVATAR_CONTAINS_NICKNAME_SUFFIX}"
        params = (nickname,)

        if exclude_unlocked_avatars:
            query += f" AND {TGOMMO_NOT_EXISTS_USER_AVATAR_ID_IN_USER_PROFILE_AVATAR_LINK_SUFFIX}"
            params += (user_id,)

        query += f" {TGOMMO_SELECT_USER_AVATAR_GROUP_BY_DISTINCT_USER_AVATAR_NICKNAME_SUFFIX};"

        return self.get_avatars_from_database(query=query, params=params, convert_to_object=convert_to_object, expect_multiple=True)

    # SHOP AVATAR QUERIES
    def get_random_shop_avatars(self, count=3, convert_to_object=True):
        query = f"{TGOMMO_SELECT_USER_AVATAR_BASE} {TGOMMO_SELECT_USER_AVATAR_BY_AVATAR_TYPE_SUFFIX} {TGOMMO_ORDER_BY_RANDOM_SUFFIX};"
        return self.get_avatars_from_database(query=query, params=('Shop', count), convert_to_object=convert_to_object,expect_multiple=True)


    # endregion

    # region INVENTORY ITEM QUERIES
    def get_inventory_item_by_item_id(self, item_id=-1, convert_to_object=True):
        query = f"{TGOMMO_GET_INVENTORY_ITEM_BASE} {TGOMMO_SELECT_INVENTORY_ITEM_BY_ITEM_ID_SUFFIX};"
        return self.get_inventory_items_from_database(query=query, params=(item_id,), convert_to_object=convert_to_object, expect_multiple=False)
    def get_inventory_item_by_user_id_and_item_id(self, user_id=0, item_id=0, item_quantity=0, convert_to_object=True):
        # todo: change this to an insert function
        self.QueryHandler.execute_query(TGOMMO_INSERT_USER_ITEM_LINK, params=(item_id, user_id, item_quantity, '1970-01-01 00:00:00', '1970-01-01 00:00:00'))

        query = f"{TGOMMO_GET_INVENTORY_ITEM_BASE} {TGOMMO_SELECT_INVENTORY_ITEM_BY_ITEM_ID_SUFFIX} AND {TGOMMO_SELECT_USER_INVENTORY_ITEM_LINK_ITEM_BY_USER_ID_SUFFIX};"
        return self.get_inventory_items_from_database(query=query, params=(item_id, user_id), convert_to_object=convert_to_object, expect_multiple=False)

    def get_inventory_item_collection_by_user_id(self, user_id=0, convert_to_object=True):
        query = f"{TGOMMO_GET_INVENTORY_ITEM_BASE} {TGOMMO_SELECT_USER_INVENTORY_ITEM_LINK_ITEM_BY_USER_ID_SUFFIX};"
        return self.get_inventory_items_from_database(query=query, params=(user_id,), convert_to_object=convert_to_object, expect_multiple=True)

    def get_rewardable_inventory_items(self, convert_to_object=True):
        query = f"{TGOMMO_GET_INVENTORY_ITEM_BASE} {TGOMMO_SELECT_INVENTORY_ITEM_BY_IS_REWARDABLE_SUFFIX};"
        return self.get_inventory_items_from_database(query=query, params=(1,), convert_to_object=convert_to_object, expect_multiple=True)

    # specific item queries
    def get_creature_inventory_expansions_by_user_id(self, user_id=0):
        self.QueryHandler.execute_query(TGOMMO_INSERT_USER_ITEM_LINK, params=(ITEM_ID_CREATURE_INVENTORY_STORAGE_EXPANSION, user_id, 8, '1970-01-01 00:00:00', '1970-01-01 00:00:00'))
        return self.get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_CREATURE_INVENTORY_STORAGE_EXPANSION, item_quantity=8).item_quantity

    # endregion

    # region COLLECTION QUERIES
    def get_collection_by_collection_id(self, convert_to_object=False):
        query = f"{TGOMMO_SELECT_COLLECTION_BASE} {TGOMMO_SELECT_COLLECTION_BY_COLLECTION_ID_SUFFIX};"
        return self.get_collections_from_database(query=query, params=(1,), convert_to_object=convert_to_object, expect_multiple=True)

    def get_active_collections(self, convert_to_object=False):
        query = f"{TGOMMO_SELECT_COLLECTION_BASE} {TGOMMO_SELECT_COLLECTION_BY_IS_ACTIVE_SUFFIX};"
        return self.get_collections_from_database(query=query, params=(1,), convert_to_object=convert_to_object, expect_multiple=True)

    # endregion


    '''' ----- UPDATE QUERIES  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # Creature Queries
    def update_creature_nickname(self, catch_id, new_nickname):
        response = self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_CREATURE_NICKNAME_BY_CATCH_ID, params=(new_nickname, catch_id))
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
        self.QueryHandler.execute_query(TGOMMO_INSERT_USER_ITEM_LINK, params=(item_id, user_id, 0, '1970-01-01 00:00:00', '1970-01-01 00:00:00'))
        response = self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_AVATAR_LINK_ITEM_COUNT, params=(new_amount, item_id, user_id))
        return response
    def update_user_avatar_item_last_purchased_date(self, user_id, item_id, last_purchased_date):
        # add a dummy record in case user hasn't obtained this item before
        self.QueryHandler.execute_query(TGOMMO_INSERT_USER_ITEM_LINK, params=(item_id, user_id, 0, '1970-01-01 00:00:00', '1970-01-01 00:00:00'))
        response = self.QueryHandler.execute_query(TGOMMO_UPDATE_USER_AVATAR_LINK_LAST_PURCHASE_DATE, params=(last_purchased_date, item_id, user_id))
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


    ''' SUPPORT FUNCTIONS '''
    def handle_user_creature_optional_query_extensions(self, base_query, params=[], user_id=None, creature_id=None, creature_dex_no=None, environment_dex_no=None, environment_variant_no=None, is_mythical=None, rarity=None, creature_class=None, is_released=None):
        if user_id and user_id != 0:
            base_query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX}"
            params.append(user_id)
        if creature_id and creature_id != 0:
            base_query += f" AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_ID_SUFFIX}"
            params.append(creature_id)
        if creature_dex_no and creature_dex_no != 0:
            base_query += f" AND {TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX}"
            params.append(creature_dex_no)
        if is_released is not None:
            base_query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_IS_RELEASED_SUFFIX}"
            params.append(1 if is_released else 0)


        # todo: need to add branching logic for  TGOMMO_SELECT_ENVIRONMENT_BY_DEX_NO_SUFFIX
        if environment_dex_no and environment_dex_no != 0:
            base_query += f" AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_DEX_NO_SUFFIX}"
            params.append(environment_dex_no)

        if rarity:
            base_query += f" AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_RARITY_SUFFIX}"
            params.append(rarity)
        if creature_class:
            base_query += f" AND {TGOMMO_SELECT_CREATURE_BY_CLASSIFICATION_SUFFIX}"
            params.append(creature_class)

        if environment_variant_no and environment_variant_no != BOTH:
            base_query += f" AND {TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_SPAWN_TIME_SUFFIX}"
            params.append(environment_variant_no)
        if is_mythical:
            base_query += f" AND {TGOMMO_SELECT_USER_CREATURE_BY_IS_MYTHICAL_SUFFIX}"
            params.append(1 if is_mythical else 0)
        return base_query, params

    def handle_environment_optional_query_extensions(self, base_query, params=[], environment_id=None, environment_dex_no=None, variant_no=None):
        if environment_id and environment_id != 0:
            base_query += f" AND {TGOMMO_SELECT_ENVIRONMENT_BY_ENVIRONMENT_ID_SUFFIX}"
            params.append(environment_id)
        if environment_dex_no and environment_dex_no != 0:
            base_query += f" AND {TGOMMO_SELECT_ENVIRONMENT_BY_DEX_NO_SUFFIX}"
            params.append(environment_dex_no)
        if variant_no and variant_no != 0:
            base_query += f" AND {TGOMMO_SELECT_ENVIRONMENT_BY_VARIANT_NO_SUFFIX}"
            params.append(variant_no)
        return base_query, params


