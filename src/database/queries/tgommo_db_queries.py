""" ----- INSERT QUERIES  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
# region INSERT QUERIES
TGOMMO_INSERT_NEW_CREATURE = """INSERT OR IGNORE INTO tgommo_creature (creature_id, name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate, default_rarity) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_ENVIRONMENT_CREATURE = """INSERT OR IGNORE INTO tgommo_environment_creature (creature_id, environment_id, spawn_time, environment_dex_no, environment_variant_no, creature_name, environment_name, spawn_rarity, local_name, sub_environment_type, local_dex_no, local_variant_no, local_img_root) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_USER_CREATURE = """INSERT INTO tgommo_user_creature(user_id, creature_id, creature_variant_no, environment_id, is_mythical, catch_date, nickname, is_released, is_favorite, is_afk_catch) VALUES(?, ?, ?, ?, ?, CURRENT_TIMESTAMP, '', 0, 0, ?) RETURNING catch_id;"""

TGOMMO_INSERT_NEW_ENVIRONMENT = """INSERT OR IGNORE INTO tgommo_environment (environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate, local_img_suffix) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

# Players
TGOMMO_INSERT_NEW_USER_PROFILE = """INSERT OR IGNORE INTO tgommo_user_profile (user_id, nickname, avatar_id, background_id, creature_slot_id_1, creature_slot_id_2, creature_slot_id_3, creature_slot_id_4, creature_slot_id_5, creature_slot_id_6, currency, available_catch_attempts, rod_level, rod_amount, trap_level, trap_amount) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_NEW_INVENTORY_ITEM = """INSERT INTO tgommo_inventory_item(item_num, item_id, item_name, item_type, item_category, item_description, rarity, is_rewardable, img_root, default_uses, shop_price) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_NEW_USER_AVATAR = """INSERT OR IGNORE INTO user_avatar (avatar_num, avatar_id, avatar_name, avatar_type, img_root, series, shop_price, unlock_startdate, unlock_enddate, is_parent_entry) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

TGOMMO_INSERT_USER_ITEM_LINK = """INSERT OR IGNORE INTO tgommo_user_item_inventory_link (item_id, user_id, item_quantity, last_used, last_purchase_date) VALUES (?, ?, ?, ?, ?);"""
TGOMMO_INSERT_USER_TRAP_LINK = """INSERT OR IGNORE INTO tgommo_user_trap_link (user_id, item_id, active_trap_mode, player_trap_charges, player_max_trap_charges, trap_scheduled_start_time, trap_scheduled_mode_end_time) VALUES (?, ?, ?, ?, ?, ?, ?);"""

TGOMMO_INSERT_NEW_USER_AVATAR_LINK = """INSERT OR IGNORE INTO tgommo_user_profile_avatar_link (avatar_id, user_id) VALUES(?, ?);"""
TGOMMO_INSERT_NEW_AVATAR_UNLOCK_CONDITION = """INSERT OR IGNORE INTO tgommo_user_avatar_unlock_condition (avatar_id, unlock_query, unlock_threshold, is_secret) VALUES(?, ?, ?, ?);"""
TGOMMO_INSERT_NEW_AVATAR_NICKNAME_LINK = """INSERT OR IGNORE INTO tgommo_user_avatar_nickname_link (avatar_id, nickname_keyword) VALUES(?, ?);"""

TGOMMO_INSERT_COLLECTION = """INSERT OR IGNORE INTO tgommo_collection (collection_id, title, description, image_path, background_color_path, total_count_query, caught_count_query, completion_reward_1, completion_reward_2, completion_reward_3, is_active) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
# endregion


''' ----- SELECT QUERIES  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
# region BASE SELECT QUERIES
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
        c.default_rarity, ec.spawn_rarity,
        ec.environment_id
    FROM tgommo_environment_creature ec 
        LEFT JOIN tgommo_creature c 
            ON c.creature_id = ec.creature_id 
    WHERE 
"""
TGOMMO_SELECT_USER_CREATURE_BASE = """
    SELECT 
        DISTINCT(uc.catch_id), c.creature_id, uc.user_id,
        c.name, c.variant_name, ec.local_name, uc.nickname, 
        c.dex_no, c.variant_no, ec.local_dex_no, ec.local_variant_no,
        c.full_name, c.scientific_name, c.kingdom, c.description, 
        c.img_root, ec.local_img_root,
        ec.environment_id, ec.sub_environment_type,
        c.encounter_rate, 
        c.default_rarity, ec.spawn_rarity, 
        uc.catch_date,
        uc.is_mythical, uc.is_released, uc.is_favorite, uc.is_afk_catch
    FROM tgommo_user_creature uc 
        LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id AND uc.environment_id = ec.environment_id 
        LEFT JOIN tgommo_creature c ON c.creature_id = ec.creature_id 
    WHERE 
"""

TGOMMO_SELECT_ENVIRONMENT_BASE = """
    SELECT 
        e.environment_id, 
        e.name, e.variant_name,
        e.dex_no, e.variant_no,
        e.location, e.description,
        e.img_root, e.local_img_suffix,
        e.is_night_environment, e.in_circulation, e.encounter_rate
    FROM tgommo_environment e
    WHERE 
"""

TGOMMO_SELECT_USER_PROFILE_BASE = '''
    SELECT
        player_id, user_id, 
        nickname, 
        avatar_id, background_id,
        creature_slot_id_1, creature_slot_id_2, creature_slot_id_3, creature_slot_id_4, creature_slot_id_5, creature_slot_id_6, 
        currency, 
        available_catch_attempts, 
        rod_level, rod_amount, trap_level, trap_amount
    FROM tgommo_user_profile up
    WHERE
'''

TGOMMO_SELECT_USER_AVATAR_BASE = '''
    SELECT
        ua.avatar_num, ua.avatar_id, 
        ua.avatar_name, ua.avatar_type, ua.series, ua.is_parent_entry,
        ua.img_root,
        auc.unlock_query, auc.unlock_threshold, auc.is_secret,
        ua.shop_price,
        ua.unlock_startdate, ua.unlock_enddate
    FROM user_avatar ua
    LEFT JOIN tgommo_user_avatar_unlock_condition auc
        ON auc.avatar_id = ua.avatar_id
    LEFT JOIN tgommo_user_profile_avatar_link upal
    	ON upal.avatar_id = ua.avatar_id
    LEFT JOIN tgommo_user_avatar_nickname_link uanl
        ON uanl.avatar_id = ua.avatar_id
    WHERE 
'''

TGOMMO_SELECT_USER_AVATAR_LINK_BASE = '''
    SELECT
        ua.avatar_num, ua.avatar_id,
        ua.avatar_name, ua.avatar_type, ua.series, ua.is_parent_entry,
        ua.img_root
    FROM user_avatar ua
    LEFT JOIN tgommo_user_profile_avatar_link upal
        ON upal.avatar_id  = ua.avatar_id
    WHERE
'''
TGOMMO_SELECT_USER_AVATAR_UNLOCK_CONDITION_BASE = '''
    SELECT
        auc.avatar_id, ua.avatar_name, ua.img_root,
        auc.unlock_query, auc.unlock_threshold, ua.is_parent_entry
    FROM tgommo_user_avatar_unlock_condition auc
    LEFT JOIN user_avatar ua
        ON ua.avatar_id = auc.avatar_id
    WHERE
'''

TGOMMO_GET_INVENTORY_ITEM_BASE = '''
    SELECT  
        ii.item_num, ii.item_id, 
        ii.item_name, ii.item_type, ii.item_category, ii.item_description, 
        ii.rarity, ii.is_rewardable, ii.img_root, ii.default_uses,
        uil.user_id, uil.item_quantity, uil.last_used, 
        uil.last_purchase_date, ii.shop_price
    FROM tgommo_inventory_item ii
    LEFT JOIN tgommo_user_item_inventory_link uil
        ON ii.item_id == uil.item_id
    WHERE  
'''
TGOMMO_SELECT_USER_INVENTORY_ITEM_LINK_BASE = """
    SELECT 
        ui.item_num, ui.item_id, 
        ui.item_name, ui.item_type, ui.item_category, ui.item_description, 
        ui.rarity, ui.is_rewardable, ui.img_root, ui.default_uses, 
        uil.item_quantity, uil.last_used, 
        uil.last_purchase_date, ii.shop_price
    FROM tgommo_user_item_inventory_link uil 
    LEFT JOIN tgommo_inventory_item ui 
        ON uil.item_id == ui.item_id 
    WHERE 
"""
TGOMMO_SELECT_USER_TRAP_LINK_BASE = """
    SELECT
        utl.user_id, utl.item_id,
        utl.active_trap_mode, utl.player_trap_charges, utl.player_max_trap_charges,
        utl.trap_scheduled_start_time, utl.trap_scheduled_mode_end_time
    FROM tgommo_user_trap_link utl
    WHERE
"""

TGOMMO_SELECT_COLLECTION_BASE = """
    SELECT
        collection_id,
        title, description,
        image_path, background_color_path,
        total_count_query, caught_count_query,
        completion_reward_1, completion_reward_2, completion_reward_3,
        is_active
    FROM tgommo_collection
    WHERE
"""
# endregion

# region CREATURE QUERIES

# region CATCH STAT QUERIES - total catches
TGOMMO_SELECT_TOTAL_CREATURES_CAUGHT_BASE = '''
    SELECT COUNT(DISTINCT(uc.catch_id)) 
    FROM tgommo_user_creature uc 
    LEFT JOIN tgommo_creature c 
        ON uc.creature_id = c.creature_id 
    LEFT JOIN tgommo_environment_creature ec 
        ON uc.creature_id = ec.creature_id
    LEFT JOIN tgommo_environment e
        ON uc.environment_id = e.environment_id
    WHERE 
'''
# endregion

# region CATCH STAT QUERIES - unique catches
TGOMMO_SELECT_UNIQUE_CREATURES_CAUGHT_BASE = '''
    SELECT COUNT(DISTINCT c.dex_no)
    FROM tgommo_user_creature uc 
    LEFT JOIN tgommo_creature c 
        ON uc.creature_id = c.creature_id 
    LEFT JOIN tgommo_environment_creature ec
        ON uc.creature_id = ec.creature_id
    WHERE 
'''
TGOMMO_SELECT_UNIQUE_CREATURE_VARIANTS_CAUGHT_BASE = '''
    SELECT COUNT(DISTINCT c.creature_id) 
    FROM tgommo_user_creature uc 
    LEFT JOIN tgommo_creature c 
        ON uc.creature_id = c.creature_id 
    LEFT JOIN tgommo_environment_creature ec
        ON uc.creature_id = ec.creature_id
    WHERE 
'''
# endregion

# region CATCH STAT QUERIES - unique catches
TGOMMO_SELECT_TOTAL_UNIQUE_CREATURES_AVAILABLE_BASE = '''
    SELECT COUNT(DISTINCT c.dex_no) 
    FROM tgommo_creature c
    LEFT JOIN tgommo_environment_creature ec 
        ON c.creature_id = ec.creature_id
    WHERE 
'''
TGOMMO_SELECT_TOTAL_UNIQUE_VARIANTS_AVAILABLE_BASE = '''
    SELECT COUNT(DISTINCT c.creature_id) 
    FROM tgommo_creature c
    LEFT JOIN tgommo_environment_creature ec 
        ON c.creature_id = ec.creature_id
    WHERE 
'''
# endregion
# endregion


# region ENCYCLOPEDIA QUERIES
TGOMMO_SELECT_FIRST_CAUGHT_VARIANT_FOR_SPECIES_BASE = """
    SELECT 
        MIN(uc.creature_variant_no) as min_variant_no
    FROM tgommo_user_creature uc
    LEFT JOIN tgommo_creature c 
        ON uc.creature_id = c.creature_id
    LEFT JOIN tgommo_environment e
        ON uc.environment_id = e.environment_id
    WHERE 
"""

TGOMMO_SELECT_USER_CREATURE_IS_RELEASED_BY_CREATURE_ID = """
    SELECT 
        is_released 
    FROM tgommo_user_creature 
    WHERE catch_id = ?;
"""

# endregion

# --------------------------------------------------------------
# OLD QUERIES, to be analyzed for removal or replacement
# --------------------------------------------------------------
# OLD QUERIES, LETS CHECK IF THESE CAN BE REPLACED!!!!!!!!


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

'''EVENT QUERIES'''
TGOMMO_GET_COUNT_FOR_SERVER_CATCHES_FOR_CREATURE_BY_CREATURE_ID = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id = ?;"""
TGOMMO_GET_TOTAL_CATCHES_BY_USER_ID = """SELECT COUNT(*) FROM tgommo_user_creature WHERE user_id = ?;"""

# endregion

# region USER QUERIES
TGOMMO_SELECT_USER_PROFILE_BY_ID = """SELECT player_id, user_id, nickname, avatar_id, background_id, creature_slot_id_1, creature_slot_id_2, creature_slot_id_3, creature_slot_id_4, creature_slot_id_5, creature_slot_id_6, currency, available_catch_attempts, rod_level, rod_amount, trap_level, trap_amount FROM tgommo_user_profile WHERE user_id = ?;"""
TGOMMO_USER_PROFILE_GET_CURRENCY_BY_USER_ID = """SELECT currency FROM tgommo_user_profile WHERE user_id = ?;"""
# endregion

# region AVATAR QUERIES
TGOMMO_AVATAR_IS_UNLOCKED_FOR_PLAYER = """SELECT count(avatar_id) FROM tgommo_user_profile_avatar_link WHERE user_id = ? AND avatar_id = ?;"""
# endregion

''' ----- UPDATE QUERIES  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
# region UPDATE QUERIES
TGOMMO_UPDATE_USER_CREATURE_NICKNAME_BY_CATCH_ID = """UPDATE tgommo_user_creature SET nickname = ? WHERE catch_id = ?;"""
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

TGOMMO_UPDATE_USER_TRAP_LINK = """UPDATE tgommo_user_trap_link SET item_id = ?, active_trap_mode = ?, player_trap_charges = ?, player_max_trap_charges = ?, trap_scheduled_start_time = ?, trap_scheduled_mode_end_time = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_TRAP_LINK_ITEM_ID = """UPDATE tgommo_user_trap_link SET item_id = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_TRAP_LINK_ACTIVE_TRAP_MODE = """UPDATE tgommo_user_trap_link SET active_trap_mode = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_TRAP_LINK_PLAYER_TRAP_CHARGES = """UPDATE tgommo_user_trap_link SET player_trap_charges = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_TRAP_LINK_PLAYER_MAX_TRAP_CHARGES = """UPDATE tgommo_user_trap_link SET player_max_trap_charges = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_TRAP_LINK_SCHEDULED_START_TIME = """UPDATE tgommo_user_trap_link SET trap_scheduled_start_time = ? WHERE user_id = ?;"""
TGOMMO_UPDATE_USER_TRAP_LINK_SCHEDULED_END_TIME = """UPDATE tgommo_user_trap_link SET trap_scheduled_mode_end_time = ? WHERE user_id = ?;"""

TGOMMO_UPDATE_USER_AVATAR_UNLOCK_STATUS = """UPDATE tgommo_user_profile_avatar_link SET user_id = ? WHERE avatar_id = ?;"""
TGOMMO_UPDATE_USER_AVATAR_LINK_ITEM_COUNT = """UPDATE tgommo_user_item_inventory_link SET item_quantity = ? WHERE item_id = ? AND user_id = ?;"""
TGOMMO_UPDATE_USER_AVATAR_LINK_LAST_PURCHASE_DATE = """UPDATE tgommo_user_item_inventory_link SET last_purchase_date = ? WHERE item_id = ? AND user_id = ?;"""
# endregion


''' ----- DELETE QUERIES  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
# region DELETE QUERIES
TGOMMO_DELETE_ALL_RECORDS_FROM_CREATURES = "DELETE FROM tgommo_creature;"
TGOMMO_DELETE_ALL_RECORDS_FROM_ENVIRONMENT_CREATURES = "DELETE FROM tgommo_environment_creature;"

TGOMMO_DELETE_ALL_RECORDS_FROM_ENVIRONMENTS = "DELETE FROM tgommo_environment;"

TGOMMO_DELETE_ALL_RECORDS_FROM_USER_AVATAR = "DELETE FROM user_avatar;"
TGOMMO_DELETE_ALL_RECORDS_FROM_INVENTORY_ITEM = "DELETE FROM tgommo_inventory_item;"

TGOMMO_DELETE_ALL_RECORDS_FROM_AVATAR_UNLOCK_CONDITIONS = "DELETE FROM tgommo_user_avatar_unlock_condition;"
TGOMMO_DELETE_ALL_RECORDS_FROM_USER_PROFILE_AVATARS_LINKS = "DELETE FROM tgommo_user_profile_avatar_link;"
TGOMMO_DELETE_ALL_RECORDS_FROM_AVATAR_NICKNAME_LINKS = "DELETE FROM tgommo_user_avatar_nickname_link;"

TGOMMO_DELETE_ALL_RECORDS_FROM_COLLECTIONS = "DELETE FROM tgommo_collection;"
# endregion


''' ----- QUERY SUFFIXES  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
# region QUERY SUFFIXES
# region tgommo_creature suffixes
TGOMMO_SELECT_CREATURE_BY_CREATURE_ID_SUFFIX = "c.creature_id = ?"
TGOMMO_SELECT_CREATURE_BY_CREATURE_DEX_NO_SUFFIX = "c.dex_no = ?"
TGOMMO_SELECT_CREATURE_BY_CREATURE_VARIANT_NO_SUFFIX = "c.variant_no = ?"
TGOMMO_SELECT_CREATURE_BY_CLASSIFICATION_SUFFIX = "c.kingdom = ?"
TGOMMO_SELECT_CREATURE_BY_EXCLUDING_TRANSCENDANT_DEFAULT_RARITY_SUFFIX = "c.default_rarity != 'Transcendant'"

TGOMMO_ORDER_BY_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX = " ORDER BY c.dex_no, c.variant_no"

TGOMMO_CATCH_ID_IN_SUFFIX = "uc.catch_id IN "
# endregion
# region tgommo_environment_creature suffixes
TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_ID_SUFFIX = "ec.environment_id = ?"
TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_DEX_NO_SUFFIX = "ec.environment_dex_no = ?"
TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_ENVIRONMENT_VARIANT_NO_SUFFIX = "ec.environment_variant_no = ?"
TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_SPAWN_TIME_SUFFIX = "ec.spawn_time = ?"
TGOMMO_SELECT_ENVIRONMENT_CREATURE_BY_RARITY_SUFFIX = "ec.spawn_rarity = ?"

TGOMMO_GROUP_BY_CREATURE_BY_CREATURE_ID_SUFFIX = "GROUP BY c.creature_id"

TGOMMO_ORDER_BY_ENVIRONMENT_CREATURE_DEX_NO_AND_VARIANT_NO_SUFFIX = " ORDER BY ec.local_dex_no, ec.local_variant_no"
# endregion
# region tgommo_user_creature suffixes
TGOMMO_SELECT_USER_CREATURE_BY_CATCH_ID_SUFFIX = "uc.catch_id = ?"
TGOMMO_SELECT_USER_CREATURE_BY_ENVIRONMENT_ID_SUFFIX = "uc.environment_id = ?"
TGOMMO_SELECT_USER_CREATURE_BY_USER_ID_SUFFIX = "uc.user_id = ?"
TGOMMO_SELECT_USER_CREATURE_BY_IS_FAVORITE_SUFFIX = "uc.is_favorite = ?"
TGOMMO_SELECT_USER_CREATURE_BY_IS_RELEASED_SUFFIX = "uc.is_released = ?"
TGOMMO_SELECT_USER_CREATURE_BY_IS_MYTHICAL_SUFFIX = "uc.is_mythical = ?"
TGOMMO_SELECT_USER_CREATURE_BY_MATCHES_ENVIRONMENT_SUFFIX = "uc.environment_id = ec.environment_id"
TGOMMO_SELECT_USER_CREATURE_BY_IS_AFK_CATCH_SUFFIX = "uc.is_afk_catch = ?"
# endregion

# region tgommo_environment suffixes
TGOMMO_SELECT_ENVIRONMENT_BY_ENVIRONMENT_ID_SUFFIX = " e.environment_id = ?"
TGOMMO_SELECT_ENVIRONMENT_BY_DEX_NO_SUFFIX = " e.dex_no = ?"
TGOMMO_SELECT_ENVIRONMENT_BY_VARIANT_NO_SUFFIX = " e.variant_no = ?"
TGOMMO_SELECT_ENVIRONMENT_BY_IN_CIRCULATION_SUFFIX = " e.in_circulation = ?"
TGOMMO_SELECT_ENVIRONMENT_BY_IS_NIGHT_ENVIRONMENT_SUFFIX = " e.is_night_environment = ?"

TGOMMO_ORDER_BY_ENVIRONMENT_DEX_NO_AND_VARIANT_NO_SUFFIX = " ORDER BY e.dex_no, e.variant_no"
TGOMMO_ORDER_BY_RANDOM_SUFFIX = " ORDER BY RANDOM() LIMIT ?"
# endregion

# region tgommo_user_profile suffixes
TGOMMO_SELECT_USER_PROFILE_BY_USER_ID_SUFFIX = " up.user_id = ?"
# endregion

# region user_avatar suffixes
TGOMMO_SELECT_USER_AVATAR_BY_AVATAR_ID_SUFFIX = " ua.avatar_id = ?"
TGOMMO_SELECT_USER_AVATAR_BY_CHILD_AVATAR_SUFFIX = " ua.avatar_id LIKE ? || '%' AND ua.avatar_id != ?"
TGOMMO_SELECT_USER_AVATAR_BY_AVATAR_TYPE_SUFFIX = "ua.avatar_type = ?"
TGOMMO_SELECT_USER_AVATAR_BY_NON_NULL_START_DATE_SUFFIX = "ua.unlock_startdate is not Null"
TGOMMO_SELECT_USER_AVATAR_BY_DATE_BETWEEN_START_AND_END_DATE_SUFFIX = "date('now') BETWEEN ua.unlock_startdate AND ua.unlock_enddate"
TGOMMO_SELECT_USER_AVATAR_GROUP_BY_DISTINCT_AVATAR_SUFFIX = " GROUP BY ua.avatar_id"
# endregion
# region user_avatar_link suffixes
TGOMMO_SELECT_USER_AVATAR_LINK_BY_USER_ID_SUFFIX = " upal.user_id = ?"
TGOMMO_SELECT_USER_AVATAR_LINK_BY_AVATAR_ID_SUFFIX = " ua.avatar_id = ?"
TGOMMO_NOT_EXISTS_USER_AVATAR_ID_IN_USER_PROFILE_AVATAR_LINK_SUFFIX = " NOT EXISTS (SELECT 1 FROM tgommo_user_profile_avatar_link upal WHERE upal.avatar_id = ua.avatar_id AND upal.user_id = ?)"
# endregion
# region tgommo_user_avatar_unlock_condition suffixes
TGOMMO_SELECT_USER_AVATAR_UNLOCK_CONDITION_BY_UNLOCK_QUERY_NOT_NULL_SUFFIX= "auc.unlock_query is not Null"
TGOMMO_SELECT_USER_AVATAR_UNLOCK_CONDITION_GROUP_BY_DISTINCT_AVATAR_SUFFIX = " GROUP BY ua.avatar_num, ua.avatar_id, ua.avatar_name, ua.avatar_type, ua.series, ua.is_parent_entry, ua.img_root"
# endregion
# region tgommo_user_avatar_nickname_link suffixes
TGOMMO_SELECT_USER_AVATAR_BY_NICKNAME_SUFFIX= "uanl.nickname_keyword = ?"
TGOMMO_SELECT_USER_AVATAR_CONTAINS_NICKNAME_SUFFIX= " ? LIKE '%' || uanl.nickname_keyword || '%'"
TGOMMO_SELECT_USER_AVATAR_GROUP_BY_DISTINCT_USER_AVATAR_NICKNAME_SUFFIX = " GROUP BY uanl.avatar_id"
# endregion

# region tgommo_inventory_item suffixes
TGOMMO_SELECT_INVENTORY_ITEM_BY_ITEM_ID_SUFFIX = " ii.item_id = ?"
TGOMMO_SELECT_INVENTORY_ITEM_BY_IS_REWARDABLE_SUFFIX = " ii.is_rewardable = ?"
# endregion
# region tgommo_user_item_inventory_link suffixes
TGOMMO_SELECT_USER_INVENTORY_ITEM_LINK_ITEM_BY_USER_ID_SUFFIX = " uil.user_id = ?"
TGOMMO_SELECT_USER_INVENTORY_ITEM_LINK_ITEM_BY_ITEM_ID_SUFFIX = " uil.item_id = ?"
# endregion
# region tgommo_user_trap_link suffixes
TGOMMO_SELECT_USER_TRAP_LINK_BY_USER_ID_SUFFIX = " utl.user_id = ?"
TGOMMO_SELECT_USER_TRAP_LINK_BY_ITEM_ID_SUFFIX = " utl.item_id = ?"
TGOMMO_SELECT_USER_TRAP_LINK_BY_SCHEDULED_START_TIME_SUFFIX = " utl.trap_scheduled_start_time = ?"
TGOMMO_SELECT_USER_TRAP_LINK_BY_SCHEDULED_END_TIME_SUFFIX = " utl.trap_scheduled_mode_end_time = ?"
# endregion

# region tgommo_collection suffixes
TGOMMO_SELECT_COLLECTION_BY_COLLECTION_ID_SUFFIX = "collection_id = ?"
TGOMMO_SELECT_COLLECTION_BY_IS_ACTIVE_SUFFIX = "is_active = ?"
# endregion
# endregion
