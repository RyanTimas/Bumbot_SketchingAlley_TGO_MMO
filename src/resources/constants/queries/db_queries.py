'''*******************'''
'''*******************'''
'''     USER Queries       '''
'''*******************'''
'''*******************'''
SA_USERS_INSERT_NEW_RECORD = """INSERT INTO users (user_id, user_name, total_xp, level, guts, hearts, smarts, will) VALUES(?, ?, ?, ?, ?, ?, ?, ?);"""

SA_USERS_SELECT_ALL = "SELECT * FROM users"
SA_USERS_SELECT_ALL_BY_USERID = "SELECT * FROM users WHERE user_id=?"

SA_USERS_UPDATE_XP = "UPDATE users SET total_xp=? WHERE user_id=?"
SA_USERS_UPDATE_LEVEL = "UPDATE users SET level=? WHERE user_id=?"
SA_USERS_UPDATE_PLAYER_STATS = "UPDATE users SET guts=?, hearts=?,smarts=?,will=? WHERE user_id=?"

SA_USERS_DELETE_BY_USERID = "DELETE FROM users WHERE user_id=?"


'''*******************'''
'''*******************'''
''' TGO MMO QUERIES  '''
'''*******************'''
'''*******************'''

'''============='''
'''SELECT QUERIES'''
'''============='''

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CREATURE QUERIES
TGOMMO_SELECT_CREATURE_BASE = '''
    SELECT 
        c.creature_id, 
        c.name, c.variant_name, 
        c.dex_no, c.variant_no, 
        c.full_name, c.scientific_name, c.kingdom, c.description, 
        c.img_root, 
        c.encounter_rate, c.default_rarity
    FROM tgommo_creature c
    WHERE
'''
TGOMMO_SELECT_ENVIRONMENT_CREATURE_BASE = """
    SELECT 
        DISTINCT(c.creature_id), 
        c.name, c.variant_name, ec.local_name,
        c.dex_no, c.variant_no, ec.local_dex_no, ec.local_variant_no,
        c.full_name, c.scientific_name, c.kingdom, c.description, 
        c.img_root, ec.local_img_root,
        ec.sub_environment_type, 
        c.encounter_rate, 
        c.default_rarity, ec.spawn_rarity 
    FROM tgommo_environment_creature ec 
        LEFT JOIN tgommo_creature c 
            ON c.creature_id = ec.creature_id 
    WHERE 
"""
TGOMMO_SELECT_USER_CREATURE_BASE = """
    SELECT 
        DISTINCT(uc.catch_id), c.creature_id, 
        c.name, c.variant_name, ec.local_name, uc.nickname, 
        c.dex_no, c.variant_no, ec.local_dex_no, ec.local_variant_no,
        c.full_name, c.scientific_name, c.kingdom, c.description, 
        c.img_root, ec.local_img_root,
        ec.sub_environment_type, 
        c.encounter_rate, 
        c.default_rarity, ec.spawn_rarity, uc.is_mythical, 
        uc.catch_date, uc.is_favorite, uc.is_released 
    FROM tgommo_user_creature uc 
        LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id AND uc.environment_id = ec.environment_id 
        LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id 
    WHERE 
"""

# creature WHERE suffixes
TGOMMO_SELECT_CREATURE_PLACEHOLDER_SUFFIX = "true"
TGOMMO_SELECT_CREATURE_BY_CREATURE_ID_SUFFIX = "c.creature_id = ?"
TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX = "c.dex_no = ?"
TGOMMO_SELECT_CREATURE_BY_CREATURE_VARIANT_NO_SUFFIX = "c.variant_no = ?"

TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_ID_SUFFIX = "ec.environment_id = ?"
TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_DEX_NO_SUFFIX = "ec.environment_dex_no = ?"
TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_VARIANT_NO_SUFFIX = "ec.environment_variant_no = ?"
TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_SPAWN_TIME_SUFFIX = "ec.spawn_time = ?"

TGOMMO_SELECT_USER_CREATURE_BY_CATCH_ID_SUFFIX = "uc.catch_id = ?"
TGOMMO_SELECT_USER_CREATURE_BY_ENVIRONMENT_ID_SUFFIX = "uc.environment_id = ?"
TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX = "uc.user_id = ?"
TGOMMO_SELECT_USER_CREATURE_BY_IS_FAVORITE_SUFFIX = "uc.is_favorite = ?"
TGOMMO_SELECT_USER_CREATURE_BY_IS_RELEASED_SUFFIX = "uc.is_released = ?"
TGOMMO_SELECT_USER_CREATURE_BY_IS_MYTHICAL_SUFFIX = "uc.is_mythical = ?"

# creature ORDER BY suffixes
TGOMMO_ORDER_BY_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX = " ORDER BY c.dex_no, c.variant_no"
TGOMMO_ORDER_BY_ENVIRONMENT_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX = " ORDER BY ec.local_dex_no, ec.local_variant_no"

'''ENCYCLOPEDIA QUERIES'''
# retrieves the total number of catches and distinct creatures caught by a user
TGOMMO_SELECT_ALL_CREATURES_CAUGHT_TOTALS_BASE = """
    SELECT 
        COUNT(*) as total_catches,
        COUNT(DISTINCT c.dex_no) as distinct_creatures_caught,
        COUNT(DISTINCT ec.creature_id) as distinct_creature_variants_caught
    FROM tgommo_user_creature uc
    LEFT JOIN  tgommo_creature c
        ON uc.creature_id = c.creature_id
    LEFT JOIN tgommo_environment_creature ec 
        ON uc.creature_id = ec.creature_id
    WHERE true
"""
# retrieves how many catches and mythical catches a user has for a particular creature
TGOMMO_SELECT_CREATURE_CAUGHT_TOTAL_BASE = """
    SELECT 
        COUNT(*) as total_catches,
        COALESCE(SUM(CASE WHEN uc.is_mythical = 1 THEN 1 ELSE 0 END), 0) as total_mythical_catches
    FROM tgommo_user_creature uc
    LEFT JOIN tgommo_environment e 
        ON uc.environment_id = e.environment_id
    LEFT JOIN tgommo_creature c
        ON uc.creature_id = c.creature_id
    WHERE true
"""

# retrieves how many unique creatures, how many unique variants, and how many unique mythical creatures a user has caught for a particular environment
TGOMMO_SELECT_USER_CATCHES_FOR_ENCYCLOPEDIA_BASE = """
    SELECT 
        COUNT(DISTINCT(c.dex_no)) as base_creatures_count,
        COUNT(DISTINCT(uc.creature_id)) as total_variants_count,
        COUNT(DISTINCT CASE WHEN uc.is_mythical = 1 THEN c.dex_no END) as mythical_base_creatures_count
    FROM tgommo_user_creature uc 
    LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id
    LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id
    WHERE true
"""
# retrieves how many unique creatures, how many unique variants, and how many unique mythical creatures are available to be caught in a particular environment
TGOMMO_SELECT_POSSIBLE_CATCHES_FOR_ENCYCLOPEDIA_BASE = """
    SELECT 
        COUNT(DISTINCT(c.dex_no)) as base_creatures_count,
        COUNT(DISTINCT(ec.creature_id)) as total_variants_count,
        COUNT(DISTINCT(c.dex_no)) as mythical_base_creatures_count
    FROM tgommo_environment_creature ec 
    LEFT JOIN tgommo_creature c ON ec.creature_id = c.creature_id
    WHERE true
"""

TGOMMO_SELECT_FIRST_CAUGHT_VARIANT_FOR_SPECIES_BASE = """
    SELECT 
        MIN(uc.creature_variant_no) as min_variant_no
    FROM tgommo_user_creature uc
    LEFT JOIN tgommo_creature c 
        ON uc.creature_id = c.creature_id
    LEFT JOIN tgommo_environment e
        ON uc.environment_id = e.environment_id
    WHERE c.dex_no = ?
"""

'''EVENT QUERIES'''
TGOMMO_SELECT_EVENT_CREATURES_FROM_ENVIRONMENT_BASE = """
    SELECT 
        creature_id, 
        name, variant_name, 
        dex_no, variant_no, 
        full_name, scientific_name, kingdom, description, 
        img_root, 
        encounter_rate, 
        default_rarity 
    FROM tgommo_creature 
    WHERE creature_id 
    IN 
"""
TGOMMO_SELECT_ENVENT_CREATURE_BY_ENVIRONMENT_ID_AND_CREATURE_ID = """
    SELECT 
        ec.creature_id, 
        ec.creature_name, ec.local_name, c.variant_name, 
        c.dex_no, c.variant_no, ec.local_dex_no, ec.local_variant_no,
        c.full_name, c.scientific_name, c.kingdom, c.description, 
        c.img_root, ec.local_img_root,
        ec.sub_environment_type, 
        c.encounter_rate, 
        ec.spawn_rarity 
    FROM tgommo_environment_creature ec 
        LEFT JOIN tgommo_creature c 
            ON c.creature_id = ec.creature_id 
    WHERE ec.creature_id = ? AND ec.environment_id = ?;
"""


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ENVIRONMENT QUERIES
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
TGOMMO_SELECT_ENVIRONMENT_BASE = """
    SELECT 
        e.environment_id, 
        e.name, e.variant_name,
        e.dex_no, e.variant_no,
        e.location, e.description,
        e.img_root,
        e.is_night_environment, 
        e.in_circulation,
        e.encounter_rate
    FROM tgommo_environment e
    WHERE
"""

# environment WHERE suffixes
TGOMMO_SELECT_ENVIRONMENT_BY_ENVIRONMENT_ID_SUFFIX = " e.environment_id = ?"
TGOMMO_SELECT_ENVIRONMENT_BY_DEX_NO_SUFFIX = " e.dex_no = ?"
TGOMMO_SELECT_ENVIRONMENT_BY_VARIANT_NO_SUFFIX = " e.variant_no = ?"
TGOMMO_SELECT_ENVIRONMENT_BY_IN_CIRCULATION_SUFFIX = " e.in_circulation = ?"
TGOMMO_SELECT_ENVIRONMENT_BY_IS_NIGHT_ENVIRONMENT_SUFFIX = " e.is_night_environment = ?"

# environment ORDER BY suffixes
TGOMMO_ORDER_BY_ENVIRONMENT_DEX_NO_AND_VARIANT_NO_SUFFIX = " ORDER BY e.dex_no, e.variant_no"
TGOMMO_ORDER_BY_RANDOM_SUFFIX = " ORDER BY RANDOM() LIMIT 1;"

TGOMMO_SELECT_USER_PROFILE_BY_ID = """SELECT player_id, user_id, nickname, avatar_id, background_id, creature_slot_id_1, creature_slot_id_2, creature_slot_id_3, creature_slot_id_4, creature_slot_id_5, creature_slot_id_6, currency, available_catch_attempts, rod_level, rod_amount, trap_level, trap_amount FROM tgommo_user_profile WHERE user_id = ?;"""


''' Get Creature/Environments By Dex No Queries'''
# Individual Creature Select Queries
TGOMMO_SELECT_CREATURE_BY_DEX_AND_VARIANT_NUMBER = """
    SELECT 
        creature_id, 
        name, variant_name, 
        dex_no, variant_no, 
        full_name, scientific_name, kingdom, description, 
        img_root, 
        encounter_rate 
    FROM tgommo_creature 
    WHERE 
        dex_no = ? 
        AND variant_no = ?
"""
TGOMMO_SELECT_CREATURES_FROM_SPECIFIED_ENVIRONMENT = """SELECT c.dex_no, c.variant_no, ce.local_name, ce.spawn_rarity, ce.sub_environment_type, ce.local_img_root, ce.local_dex_no, ce.local_variant_no FROM tgommo_creature c JOIN tgommo_environment_creature ce ON c.creature_id = ce.creature_id WHERE ce.environment_id = ? ORDER BY dex_no, variant_no"""

TGOMMO_SELECT_USER_CREATURES_BY_USER_ID = """
    SELECT 
        DISTINCT(uc.catch_id), 
        uc.creature_id, 
        ec.creature_name, ec.local_name, uc.nickname, c.variant_name, 
        c.dex_no, c.variant_no, ec.local_dex_no, ec.local_variant_no,
        c.full_name, c.scientific_name, c.kingdom, c.description, 
        c.img_root, ec.local_img_root,
        ec.sub_environment_type, 
        c.encounter_rate, 
        ec.spawn_rarity, uc.is_mythical, 
        uc.catch_date, uc.is_favorite, uc.is_released 
    FROM tgommo_user_creature uc 
        LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id AND uc.environment_id = ec.environment_id 
        LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id 
    WHERE uc.user_id = ? AND uc.is_released = 0;
"""

TGOMMO_SELECT_USER_CREATURE_BY_CATCH_ID = """
    SELECT 
        uc.catch_id,  uc.creature_id, 
        ec.creature_name, ec.local_name, uc.nickname, c.variant_name, 
        c.dex_no, c.variant_no, ec.local_dex_no, ec.local_variant_no, 
        c.full_name, c.scientific_name, c.kingdom, c.description, 
        c.img_root,  ec.local_img_root, 
        ec.sub_environment_type, c.encounter_rate, 
        ec.spawn_rarity,  uc.is_mythical,
        uc.catch_date, uc.is_favorite, uc.is_released
    FROM tgommo_user_creature uc 
        LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id 
        LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id 
    WHERE uc.catch_id = ?;
"""


TGOMMO_SELECT_USER_CREATURES_BY_USER_ID_AND_ENVIRONMENT_ID = """SELECT uc.catch_id, uc.creature_id, ec.creature_name, ec.local_name, uc.nickname, c.variant_name, c.dex_no, c.variant_no, c.full_name, c.scientific_name, c.kingdom, c.description, c.img_root, ec.sub_environment_type, c.encounter_rate, ec.spawn_rarity, uc.creature_id, uc.creature_variant_no, uc.is_mythical FROM tgommo_user_creature uc LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id WHERE uc.user_id = ? AND uc.environment_id = ?"""
TGOMMO_SELECT_USER_CREATURE_IS_RELEASED_BY_CREATURE_ID = """SELECT is_released FROM tgommo_user_creature WHERE catch_id = ?;"""

TGOMMO_SELECT_DISPLAY_CREATURES_FOR_PLAYER_PROFILE_PAGE = """SELECT c.creature_id,uc.nickname, ec.creature_name, ec.local_name, c.variant_name,c.dex_no,c.variant_no,c.full_name,c.scientific_name,c.kingdom,c.description,c.img_root,c.encounter_rate,ec.spawn_rarity,uc.is_mythical from tgommo_user_creature uc  LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id AND uc.environment_id = ec.environment_id  LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id AND uc.creature_variant_no = c.variant_no WHERE uc.catch_id IN (?, ?, ?, ?, ?, ?);"""
TGOMMO_SELECT_DISPLAY_CREATURE_FOR_PLAYER_PROFILE_PAGE = """
    SELECT 
        uc.catch_id, c.creature_id,
        ec.creature_name, ec.local_name, uc.nickname, c.variant_name,
        c.dex_no, c.variant_no, ec.local_dex_no, ec.local_variant_no,
        c.full_name, c.scientific_name, c.kingdom, c.description,
        c.img_root, ec.local_img_root,
        ec.sub_environment_type, 
        c.encounter_rate,
        ec.spawn_rarity, uc.is_mythical, 
        uc.catch_date,  uc.is_favorite, uc.is_released
    FROM tgommo_user_creature uc  
        LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id AND uc.environment_id = ec.environment_id  
        LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id AND uc.creature_variant_no = c.variant_no 
    WHERE uc.catch_id IN (?);"""

TGOMMO_SELECT_RELEASED_CREATURES_BY_USER_ID = """
    SELECT 
        uc.catch_id, uc.creature_id, 
        ec.creature_name, ec.local_name, uc.nickname, c.variant_name, 
        c.dex_no, c.variant_no, ec.local_dex_no, ec.local_variant_no, 
        c.full_name, c.scientific_name, c.kingdom, c.description, 
        c.img_root, ec.local_img_root,
        ec.sub_environment_type, 
        c.encounter_rate, 
        ec.spawn_rarity, uc.is_mythical, 
        uc.catch_date, uc.is_favorite, uc.is_released
    FROM tgommo_user_creature uc 
        LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id 
        LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id 
    WHERE 
        uc.user_id = ? 
        AND uc.is_released = 1;
"""

# Environment Select Queries
TGOMMO_GET_RANDOM_ENVIRONMENT_IN_ROTATION = """SELECT environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate FROM tgommo_environment WHERE in_circulation = 1 ORDER BY RANDOM() LIMIT 1;"""
TGOMMO_GET_RANDOM_ENVIRONMENT_IN_ROTATION_FOR_SPECIFIC_TIME_OF_DAY = """SELECT environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate FROM tgommo_environment WHERE in_circulation = 1 AND is_night_environment = ? ORDER BY RANDOM() LIMIT 1;"""
TGOMMO_SELECT_ENVIRONMENT_BY_DEX_AND_VARIANT_NUMBER = """SELECT environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate FROM tgommo_environment WHERE dex_no = ? AND variant_no = ?"""
TGOMMO_SELECT_RANDOM_ENVIRONMENT_ID = """SELECT environment_id FROM tgommo_environment WHERE in_circulation = 1 ORDER BY RANDOM() LIMIT 1"""
TGOMMO_GET_ALL_ENVIRONMENTS_IN_ROTATION = """SELECT environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate FROM tgommo_environment WHERE in_circulation = 1 AND variant_no = 1;"""

# Player Select Queries
TGOMMO_SELECT_USER_ITEM_BY_USER_ID_AND_ITEM_ID = """SELECT ui.item_num, ui.item_id, ui.item_name, ui.item_type, ui.item_description, ui.rarity, ui.is_rewardable, ui.img_root, ui.default_uses, uil.item_quantity, uil.last_used FROM tgommo_user_item_inventory_link uil LEFT JOIN tgommo_inventory_item ui ON uil.item_id == ui.item_id WHERE uil.user_id = ? AND uil.item_id=?;"""
TGOMMO_SELECT_USER_ITEMS_BY_USER_ID = """
    SELECT 
        ui.item_num, 
        ui.item_id, 
        ui.item_name, 
        ui.item_type, 
        ui.item_description, 
        ui.rarity, 
        ui.is_rewardable, 
        ui.img_root, 
        ui.default_uses, 
        uil.item_quantity, 
        uil.last_used 
    FROM tgommo_user_item_inventory_link uil 
    LEFT JOIN tgommo_inventory_item ui 
        ON uil.item_id == ui.item_id 
    WHERE uil.user_id = ?
        AND ui.item_type not in ('Gameplay Mechanics');
"""
TGOMMO_USER_PROFILE_GET_CURRENCY_BY_USER_ID = """SELECT currency FROM tgommo_user_profile WHERE user_id = ?;"""

TGOMMO_GET_COUNT_FOR_USER_CATCHES_FOR_CREATURE_BY_DEX_NUM = """SELECT COUNT(*) FROM tgommo_user_creature uc JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE uc.user_id = ? AND c.dex_no = ?;"""
TGOMMO_HAS_USER_CAUGHT_SPECIES = """SELECT COUNT(*) == 0 FROM tgommo_user_creature WHERE user_id = ? AND creature_id = ?;"""

TGOMMO_GET_SERVER_MYTHICAL_COUNT = '''SELECT COUNT(*) FROM  tgommo_user_creature WHERE is_mythical = 1'''
TGOMMO_GET_COUNT_FOR_SERVER_CATCHES_FOR_CREATURE_BY_CREATURE_ID = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id = ?;"""

TGOMMO_GET_TOTAL_CATCHES_BY_USER_ID = """SELECT COUNT(*) FROM tgommo_user_creature WHERE user_id = ?;"""

TGOMMO_GET_RARITY_FOR_CREATURE_BY_CREATURE_ID_AND_ENVIRONMENT_ID = """select ec.spawn_rarity from tgommo_environment_creature where creature_id = ? and environment_id = ?;"""
TGOMMO_GET_RARITY_FOR_CREATURE_BY_CREATURE_ID_AND_ENVIRONMENT_DEX_NO = """SELECT spawn_rarity FROM tgommo_environment_creature ec LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id where ec.creature_id = ? and e.dex_no = ?;"""

TGOMMO_GET_IDS_FOR_UNIQUE_CREATURES = """select creature_id from tgommo_creature where variant_no = 1;"""

""" COLLECTION QUERIES """
TGOMMO_GET_ALL_ACTIVE_COLLECTIONS = """SELECT collection_id, title, description, image_path, background_color_path, total_count_query, caught_count_query, completion_reward_1, completion_reward_2, completion_reward_3, is_active FROM tgommo_collection WHERE is_active = 1;"""
TGOMMO_GET_COLLECTION_BY_ID = """SELECT collection_id, title, description, image_path , background_color_path, total_count_query, caught_count_query, completion_reward_1, completion_reward_2, completion_reward_3 FROM tgommo_collection WHERE collection_id = ? AND is_active = 1;"""

'''Environment Collection Challenge Queries'''
TGOMMO_COLLECTION_QUERY_ALL_CREATURES_TOTAL = """SELECT COUNT(DISTINCT ec.creature_id) FROM tgommo_environment_creature ec LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id ;"""
TGOMMO_COLLECTION_QUERY_ALL_CREATURES_CAUGHT = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_environment e ON uc.environment_id = e.environment_id WHERE user_id=?;"""

TGOMMO_COLLECTION_QUERY_US_EAST_TOTAL = """SELECT COUNT(DISTINCT ec.creature_id) FROM tgommo_environment_creature ec LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id WHERE e.dex_no =1;"""
TGOMMO_COLLECTION_QUERY_US_EAST_CAUGHT = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_environment e ON uc.environment_id = e.environment_id WHERE e.dex_no =1 AND user_id=?;"""

'''Creature Collection Challenge Queries'''
TGOMMO_COLLECTION_QUERY_MAMMAL_TOTAL = """SELECT Count(Distinct ec.creature_id) FROM tgommo_environment_creature ec LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id WHERE c.kingdom = "Mammal";"""
TGOMMO_COLLECTION_QUERY_MAMMAL_CAUGHT = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE c.kingdom = "Mammal" AND uc.user_id = ?;"""

TGOMMO_COLLECTION_QUERY_BIRD_TOTAL = """SELECT Count(Distinct ec.creature_id) FROM tgommo_environment_creature ec LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id WHERE c.kingdom = "Bird";"""
TGOMMO_COLLECTION_QUERY_BIRD_CAUGHT = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE c.kingdom = "Bird" AND uc.user_id = ?;"""

TGOMMO_COLLECTION_QUERY_REPTILE_TOTAL = """SELECT Count(Distinct ec.creature_id) FROM tgommo_environment_creature ec LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id WHERE c.kingdom = "Reptile";"""
TGOMMO_COLLECTION_QUERY_REPTILE_CAUGHT = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE c.kingdom = "Reptile" AND uc.user_id = ?;"""

TGOMMO_COLLECTION_QUERY_AMPHIBIAN_TOTAL = """SELECT Count(Distinct ec.creature_id) FROM tgommo_environment_creature ec LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id WHERE c.kingdom = "Amphibian";"""
TGOMMO_COLLECTION_QUERY_AMPHIBIAN_CAUGHT = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE c.kingdom = "Amphibian" AND uc.user_id = ?;"""

TGOMMO_COLLECTION_QUERY_BUG_TOTAL = """SELECT Count(Distinct ec.creature_id) FROM tgommo_environment_creature ec LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id WHERE c.kingdom IN ("Insect", "Arachnid");"""
TGOMMO_COLLECTION_QUERY_BUG_CAUGHT = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE c.kingdom IN ("Insect", "Arachnid") AND uc.user_id = ?;"""

TGOMMO_COLLECTION_QUERY_MYTHICAL_TOTAL = """SELECT COUNT(DISTINCT creature_id) FROM tgommo_environment_creature ec LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id;"""
TGOMMO_COLLECTION_QUERY_MYTHICAL_CAUGHT = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc  LEFT JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE uc.is_mythical=1 AND user_id=?;"""

TGOMMO_COLLECTION_QUERY_VARIANTS_TOTAL = """SELECT COUNT(DISTINCT c.creature_id) FROM tgommo_creature c WHERE c.variant_no != 1;"""
TGOMMO_COLLECTION_QUERY_VARIANTS_CAUGHT = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE uc.creature_variant_no!=1 AND user_id=?;"""


""" AVATAR QUERIES """
TGOMMO_SELECT_AVATAR_BY_ID = """SELECT avatar_num, avatar_id, avatar_name, avatar_type, img_root, series, is_parent_entry FROM user_avatar WHERE avatar_id = ?;"""

TGOMMO_AVATAR_GET_UNLOCKED_AVATARS_FOR_SERVER = """SELECT avatar_num, avatar_id, avatar_name, avatar_type, img_root, series FROM user_avatar ua LEFT JOIN tgommo_user_profile_avatar_link upal ON upal.avatar_id  = ua.avatar_id WHERE upal.user_id = -1;"""
TGOMMO_AVATAR_GET_UNLOCKED_AVATARS_BY_USER_ID = """SELECT ua.avatar_num, ua.avatar_id, ua.avatar_name, ua.avatar_type, ua.img_root, ua.series FROM user_avatar ua LEFT JOIN tgommo_user_profile_avatar_link upal ON upal.avatar_id  = ua.avatar_id WHERE upal.user_id IN (-1, ?);"""
TGOMMO_AVATAR_GET_UNLOCKED_AVATARS_BY_USER_ID_ORDERED_BY_AVATAR_TYPE = """SELECT ua.avatar_num, ua.avatar_id, ua.avatar_name, ua.avatar_type, ua.img_root, ua.series FROM user_avatar ua LEFT JOIN tgommo_user_profile_avatar_link upal ON upal.avatar_id  = ua.avatar_id WHERE upal.user_id IN (-1, ?) ORDER BY CASE avatar_type WHEN 'Default' THEN 1 WHEN 'Secret' THEN 2 WHEN 'Event' THEN 3 WHEN 'Quest' THEN 4 WHEN 'Transcendant' THEN 5 ELSE 6 END;"""

TGOMMO_AVATAR_IS_UNLOCKED_FOR_SERVER = """SELECT count(avatar_id) FROM tgommo_user_profile_avatar_link WHERE user_id = -1 AND avatar_id = ?;"""
TGOMMO_AVATAR_IS_UNLOCKED_FOR_PLAYER = """SELECT count(avatar_id) FROM tgommo_user_profile_avatar_link WHERE user_id = ? AND avatar_id = ?;"""

TGOMMO_GET_ALL_AVATAR_UNLOCK_CONDITIONS = """SELECT auc.avatar_id, ua.avatar_name, ua.img_root, auc.unlock_query, auc.unlock_threshold, ua.is_parent_entry, auc.is_secret FROM tgommo_user_avatar_unlock_condition auc LEFT JOIN user_avatar ua ON ua.avatar_id = auc.avatar_id;"""
TGOMMO_GET_ALL_CHILD_AVATARS_FOR_PARENT_AVATAR_ID = """SELECT avatar_num, avatar_id, avatar_name, avatar_type, img_root, series FROM user_avatar WHERE avatar_id LIKE ? || '%' AND avatar_id != ?;"""

"""ITEM QUERIES"""
TGOMMO_GET_ALL_INVENTORY_ITEMS = """SELECT item_num, item_id, item_name, item_type, item_description, rarity, is_rewardable, img_root, default_uses FROM tgommo_inventory_item;"""
TGOMMO_GET_ALL_REWARDABLE_INVENTORY_ITEMS = """SELECT item_num, item_id, item_name, item_type, item_description, rarity, is_rewardable, img_root, default_uses FROM tgommo_inventory_item WHERE is_rewardable=1;"""
TGOMMO_GET_INVENTORY_ITEM_BY_ITEM_ID = """SELECT item_num, item_id, item_name, item_type, item_description, rarity, is_rewardable, img_root, default_uses FROM tgommo_inventory_item WHERE item_id=?;"""

TGOMMO_GET_USER_ITEM_AMOUNT_BY_USER_ID_AND_ITEM_ID = """SELECT item_quantity FROM tgommo_user_item_inventory_link WHERE user_id = ? AND item_id = ?;"""

'''============='''
'''UPDATE QUERIES'''
'''============='''

TGOMMO_UPDATE_CREATURE_NICKNAME_BY_CATCH_ID = """UPDATE tgommo_user_creature SET nickname = ? WHERE catch_id = ?;"""

TGOMMO_UPDATE_USER_CREATURE_IS_RELEASED = """UPDATE tgommo_user_creature SET is_released = ? WHERE catch_id = ?;"""
TGOMMO_UPDATE_USER_CREATURE_IS_FAVORITE = """UPDATE tgommo_user_creature SET is_favorite = ? WHERE catch_id = ?;"""

TGOMMO_UPDATE_USER_PROFILE = """UPDATE tgommo_user_profile SET nickname=?, avatar_id=?, background_id=?, creature_slot_id_1=?, creature_slot_id_2=?, creature_slot_id_3=?, creature_slot_id_4=?, creature_slot_id_5=?, creature_slot_id_6=?, currency=?, available_catch_attempts=?, rod_level=?, rod_amount=?, trap_level=?, trap_amount=? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_NICKNAME = """UPDATE tgommo_user_profile SET nickname = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_CREATURE_1 = """UPDATE tgommo_user_profile SET creature_slot_id_1 = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_CREATURE_2 = """UPDATE tgommo_user_profile SET creature_slot_id_2 = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_CREATURE_3 = """UPDATE tgommo_user_profile SET creature_slot_id_3 = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_CREATURE_4 = """UPDATE tgommo_user_profile SET creature_slot_id_4 = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_CREATURE_5 = """UPDATE tgommo_user_profile SET creature_slot_id_5 = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_CREATURE_6 = """UPDATE tgommo_user_profile SET creature_slot_id_6 = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_CURRENCY = """UPDATE tgommo_user_profile SET currency = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_AVAILABLE_CATCH_ATTEMPTS = """UPDATE tgommo_user_profile SET available_catch_attempts = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_ROD_LEVEL = """UPDATE tgommo_user_profile SET rod_level = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_ROD_AMOUNT = """UPDATE tgommo_user_profile SET rod_amount = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_TRAP_LEVEL = """UPDATE tgommo_user_profile SET trap_level = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_TRAP_AMOUNT = """UPDATE tgommo_user_profile SET trap_amount = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_PROFILE_DISPLAY_CREATURES = """UPDATE tgommo_user_profile SET creature_slot_id_1 = ?, creature_slot_id_2 = ?, creature_slot_id_3 = ?, creature_slot_id_4 = ?, creature_slot_id_5 = ?,creature_slot_id_6 = ? WHERE user_id = ?;"""

TGOMMO_UPDATE_USER_AVATAR_UNLOCK_STATUS = """UPDATE tgommo_user_profile_avatar_link SET user_id = ? WHERE avatar_id = ?;"""

TGOMMO_UPDATE_USER_AVATAR_LINK_ITEM_COUNT = """UPDATE tgommo_user_item_inventory_link SET item_quantity = ? WHERE item_id = ? AND user_id = ?;"""


'''============='''
'''INSERT QUERIES'''
'''============='''

# Basic Object Tables
TGOMMO_INSERT_NEW_CREATURE = """INSERT OR IGNORE INTO tgommo_creature (creature_id, name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate, default_rarity) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_NEW_ENVIRONMENT = """INSERT OR IGNORE INTO tgommo_environment (environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

TGOMMO_INSERT_NEW_USER_PROFILE = """INSERT OR IGNORE INTO tgommo_user_profile (user_id, nickname, avatar_id, background_id, creature_slot_id_1, creature_slot_id_2, creature_slot_id_3, creature_slot_id_4, creature_slot_id_5, creature_slot_id_6, currency, available_catch_attempts, rod_level, rod_amount, trap_level, trap_amount) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_NEW_INVENTORY_ITEM = """INSERT INTO tgommo_inventory_item(item_num, item_id, item_name, item_type, item_description, rarity, is_rewardable, img_root, default_uses) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_NEW_USER_AVATAR = """INSERT OR IGNORE INTO user_avatar (avatar_num, avatar_id, avatar_name, avatar_type, img_root, series, is_parent_entry) VALUES(?, ?, ?, ?, ?, ?, ?);"""

# Link Tables
TGOMMO_INSERT_ENVIRONMENT_CREATURE = """INSERT OR IGNORE INTO tgommo_environment_creature (creature_id, environment_id, spawn_time, environment_dex_no, environment_variant_no, creature_name, environment_name, spawn_rarity, local_name, sub_environment_type, local_dex_no, local_variant_no, local_img_root) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_USER_CREATURE = """INSERT INTO tgommo_user_creature(user_id, creature_id, creature_variant_no, environment_id, is_mythical, catch_date, nickname) VALUES(?, ?, ?, ?, ?, CURRENT_TIMESTAMP, '') RETURNING catch_id;"""

TGOMMO_INSERT_USER_ITEM_LINK = """INSERT OR IGNORE INTO tgommo_user_item_inventory_link (item_id, user_id, item_quantity, last_used) VALUES (?, ?, ?, ?);"""
TGOMMO_INSERT_NEW_USER_AVATAR_LINK = """INSERT OR IGNORE INTO tgommo_user_profile_avatar_link (avatar_id, user_id) VALUES(?, ?);"""

TGOMMO_INSERT_NEW_AVATAR_UNLOCK_CONDITION = """INSERT OR IGNORE INTO tgommo_user_avatar_unlock_condition (avatar_id, unlock_query, unlock_threshold, is_secret) VALUES(?, ?, ?, ?);"""
TGOMMO_INSERT_COLLECTION = """INSERT OR IGNORE INTO tgommo_collection (collection_id, title, description, image_path, background_color_path, total_count_query, caught_count_query, completion_reward_1, completion_reward_2, completion_reward_3, is_active) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

'''============='''
'''DELETE QUERIES'''
'''============='''

TGOMMO_DELETE_ALL_RECORDS_FROM_USER_PROFILE_AVATARS = "DELETE FROM user_avatar;"
TGOMMO_DELETE_ALL_RECORDS_FROM_USER_PROFILE_AVATARS_LINKS = "DELETE FROM tgommo_user_profile_avatar_link;"

TGOMMO_DELETE_ALL_RECORDS_FROM_ENVIRONMENTS = "DELETE FROM tgommo_environment;"

TGOMMO_DELETE_ALL_RECORDS_FROM_CREATURES = "DELETE FROM tgommo_creature;"
TGOMMO_DELETE_ALL_RECORDS_FROM_ENVIRONMENT_CREATURES = "DELETE FROM tgommo_environment_creature;"

TGOMMO_DELETE_ALL_RECORDS_FROM_COLLECTIONS = "DELETE FROM tgommo_collection;"
TGOMMO_DELETE_ALL_RECORDS_FROM_USER_AVATAR = "DELETE FROM user_avatar;"
TGOMMO_DELETE_ALL_RECORDS_FROM_AVATAR_UNLOCK_CONDITIONS = "DELETE FROM tgommo_user_avatar_unlock_condition;"
TGOMMO_DELETE_ALL_RECORDS_FROM_INVENTORY_ITEM = "DELETE FROM tgommo_inventory_item;"

