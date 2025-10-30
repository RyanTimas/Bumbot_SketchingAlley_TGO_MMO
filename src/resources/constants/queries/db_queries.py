'''*******************'''
'''   USER Queries    '''
'''*******************'''
SA_USERS_INSERT_NEW_RECORD = """INSERT INTO users (user_id, user_name, total_xp, level, guts, hearts, smarts, will) VALUES(?, ?, ?, ?, ?, ?, ?, ?);"""

SA_USERS_SELECT_ALL = "SELECT * FROM users"
SA_USERS_SELECT_ALL_BY_USERID = "SELECT * FROM users WHERE user_id=?"

SA_USERS_UPDATE_XP = "UPDATE users SET total_xp=? WHERE user_id=?"
SA_USERS_UPDATE_LEVEL = "UPDATE users SET level=? WHERE user_id=?"
SA_USERS_UPDATE_PLAYER_STATS = "UPDATE users SET guts=?, hearts=?,smarts=?,will=? WHERE user_id=?"

SA_USERS_DELETE_BY_USERID = "DELETE FROM users WHERE user_id=?"


'''*******************'''
''' TGO MMO Queries  '''
'''*******************'''

'''============='''
'''SELECT QUERIES'''
'''============='''

''' Get Creature/Environments By IDs Queries'''
TGOMMO_SELECT_CREATURE_BY_ID = """SELECT creature_id, name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate FROM tgommo_creature WHERE creature_id = ?"""
TGOMMO_SELECT_ENVIRONMENT_BY_ID = """SELECT environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate FROM tgommo_environment WHERE environment_id = ?"""
TGOMMO_SELECT_USER_PROFILE_BY_ID = """SELECT player_id, user_id, nickname, avatar_id, background_id, creature_slot_id_1, creature_slot_id_2, creature_slot_id_3, creature_slot_id_4, creature_slot_id_5, creature_slot_id_6, currency, available_catch_attempts, rod_level, rod_amount, trap_level, trap_amount FROM tgommo_user_profile WHERE user_id = ?;"""

TGOMMO_SELECT_EVENT_CREATURES_FROM_ENVIRONMENT = """SELECT creature_id, name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate, default_rarity FROM tgommo_creature WHERE creature_id IN """

''' Get Creature/Environments By Dex No Queries'''
TGOMMO_SELECT_CREATURE_BY_DEX_AND_VARIANT_NUMBER = """SELECT creature_id, name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate FROM tgommo_creature WHERE dex_no = ? AND variant_no = ?"""
TGOMMO_SELECT_ENVIRONMENT_BY_DEX_AND_VARIANT_NUMBER = """SELECT environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate FROM tgommo_environment WHERE dex_no = ? AND variant_no = ?"""
TGOMMO_SELECT_CREATURES_FROM_SPECIFIED_ENVIRONMENT = """SELECT c.dex_no, c.variant_no, ce.local_name, ce.spawn_rarity, ce.sub_environment_type FROM tgommo_creature c JOIN tgommo_environment_creature ce ON c.creature_id = ce.creature_id WHERE ce.environment_id = ? ORDER BY dex_no, variant_no"""

''' Other Get Creature/Environment Queries '''
TGOMMO_SELECT_CREATURE_BY_CATCH_ID = """SELECT uc.nickname, ec.creature_name, ec.local_name, ec.spawn_rarity, uc.creature_id, uc.creature_variant_no, uc.is_mythical from tgommo_user_creature uc LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id where uc.catch_id = ?;"""

TGOMMO_GET_CREATURE_COLLECTION_BY_USER = """SELECT uc.catch_id, uc.creature_id, COALESCE(NULLIF(ec.local_name, ''), c.name) AS display_name, c.variant_name, uc.nickname, ec.spawn_rarity, uc.is_mythical FROM tgommo_user_creature uc  LEFT JOIN tgommo_environment_creature ec ON ec.creature_id = uc.creature_id AND uc.environment_id = ec.environment_id LEFT JOIN tgommo_creature c ON ec.creature_id = c.creature_id WHERE uc.user_id = ?  ORDER BY c.dex_no, c.variant_no"""
TGOMMO_GET_CREATURE_COLLECTION_BY_USER_AND_ENVIRONMENT = """SELECT uc.catch_id, uc.creature_id, COALESCE(NULLIF(ec.local_name, ''), c.name) AS display_name, c.variant_name, uc.nickname, ec.spawn_rarity, uc.is_mythical FROM tgommo_user_creature uc  LEFT JOIN tgommo_environment_creature ec ON ec.creature_id = uc.creature_id  LEFT JOIN tgommo_creature c ON ec.creature_id = c.creature_id  WHERE uc.user_id = ?  AND uc.environment_id = ? ORDER BY c.dex_no"""

TGOMMO_SELECT_RANDOM_ENVIRONMENT_ID = """SELECT environment_id FROM tgommo_environment WHERE in_circulation = 1 ORDER BY RANDOM() LIMIT 1"""
TGOMMO_SELECT_DISPLAY_CREATURES_FOR_PLAYER_PROFILE_PAGE = """SELECT c.creature_id,uc.nickname, ec.creature_name, ec.local_name, c.variant_name,c.dex_no,c.variant_no,c.full_name,c.scientific_name,c.kingdom,c.description,c.img_root,c.encounter_rate,ec.spawn_rarity,uc.is_mythical from tgommo_user_creature uc  LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id AND uc.environment_id = ec.environment_id  LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id AND uc.creature_variant_no = c.variant_no WHERE uc.catch_id IN (?, ?, ?, ?, ?, ?);"""
TGOMMO_SELECT_DISPLAY_CREATURE_FOR_PLAYER_PROFILE_PAGE = """SELECT c.creature_id,uc.nickname, ec.creature_name, ec.local_name, c.variant_name,c.dex_no,c.variant_no,c.full_name,c.scientific_name,c.kingdom,c.description,c.img_root,c.encounter_rate,ec.spawn_rarity,uc.is_mythical, uc.catch_date from tgommo_user_creature uc  LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id AND uc.environment_id = ec.environment_id  LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id AND uc.creature_variant_no = c.variant_no WHERE uc.catch_id IN (?);"""

''' Encyclopedia & Statistics Queries '''
TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_USER = """SELECT c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no, COUNT(uc.creature_id) as total_catches, SUM(CASE WHEN uc.is_mythical = 1 THEN 1 ELSE 0 END) as mythical_catches, c.img_root FROM tgommo_creature c LEFT JOIN tgommo_user_creature uc ON c.creature_id = uc.creature_id AND uc.user_id = ? GROUP BY c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no ORDER BY c.dex_no, c.variant_no;"""
TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_USER_BY_DEX_NUM = """SELECT c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no, COUNT(uc.creature_id) as total_catches, SUM(CASE WHEN uc.is_mythical = 1 THEN 1 ELSE 0 END) as mythical_catches, c.img_root  FROM tgommo_creature c  LEFT JOIN tgommo_user_creature uc ON c.creature_id = uc.creature_id AND uc.user_id = ? LEFT JOIN tgommo_environment_creature ec ON c.creature_id = ec.creature_id  LEFT JOIN tgommo_environment e ON ec.environment_id  = e.environment_id WHERE e.dex_no  = ? GROUP BY c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no ORDER BY c.dex_no, c.variant_no;"""
TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_USER_BY_DEX_NUM_AND_VARIANT_NO = """SELECT c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no, COUNT(uc.creature_id) as total_catches, SUM(CASE WHEN uc.is_mythical = 1 THEN 1 ELSE 0 END) as mythical_catches, c.img_root FROM tgommo_creature c LEFT JOIN tgommo_user_creature uc ON c.creature_id = uc.creature_id AND uc.user_id = ? LEFT JOIN tgommo_environment_creature ec ON c.creature_id = ec.creature_id LEFT JOIN tgommo_environment e ON ec.environment_id  = e.environment_id WHERE e.dex_no  = ? AND e.variant_no = ? GROUP BY c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no ORDER BY c.dex_no, c.variant_no;"""

TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_SERVER = """SELECT c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no, COUNT(uc.creature_id) as total_catches, SUM(CASE WHEN uc.is_mythical = 1 THEN 1 ELSE 0 END) as mythical_catches, c.img_root FROM tgommo_creature c LEFT JOIN tgommo_user_creature uc ON c.creature_id = uc.creature_id GROUP BY c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no ORDER BY c.dex_no, c.variant_no;"""
TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_SERVER_FOR_ENVIRONMENT_DEX_NO = """SELECT c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no, COUNT(uc.creature_id) as total_catches, SUM(CASE WHEN uc.is_mythical = 1 THEN 1 ELSE 0 END) as mythical_catches, c.img_root FROM tgommo_creature c LEFT JOIN tgommo_user_creature uc ON c.creature_id = uc.creature_id LEFT JOIN tgommo_environment_creature ec ON c.creature_id = ec.creature_id LEFT JOIN tgommo_environment e ON ec.environment_id  = e.environment_id WHERE e.dex_no  = ? GROUP BY c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no ORDER BY c.dex_no, c.variant_no;"""
TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_SERVER_FOR_ENVIRONMENT_DEX_NO_AND_VARIANT_NO = """SELECT c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no, COUNT(uc.creature_id) as total_catches, SUM(CASE WHEN uc.is_mythical = 1 THEN 1 ELSE 0 END) as mythical_catches, c.img_root FROM tgommo_creature c LEFT JOIN tgommo_user_creature uc ON c.creature_id = uc.creature_id LEFT JOIN tgommo_environment_creature ec ON c.creature_id = ec.creature_id LEFT JOIN tgommo_environment e ON ec.environment_id  = e.environment_id WHERE e.dex_no  = ? AND e.variant_no = ? GROUP BY c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no ORDER BY c.dex_no, c.variant_no;"""

TGOMMO_GET_COUNT_FOR_USER_CATCHES_FOR_CREATURE_BY_DEX_NUM = """SELECT COUNT(*) FROM tgommo_user_creature uc JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE uc.user_id = ? AND c.dex_no = ?;"""
TGOMMO_GET_COUNT_FOR_USER_CATCHES_FOR_CREATURE_BY_DEX_NUM_AND_VARIANT_NUM = """SELECT COUNT(*) FROM tgommo_user_creature uc JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE uc.user_id = ? AND c.dex_no = ? AND c.variant_no = ?;"""
TGOMMO_HAS_USER_CAUGHT_SPECIES = """SELECT COUNT(*) == 0 FROM tgommo_user_creature WHERE user_id = ? AND creature_id = ?;"""

TGOMMO_GET_SERVER_MYTHICAL_COUNT = '''SELECT COUNT(*) FROM  tgommo_user_creature WHERE is_mythical = 1'''
TGOMMO_GET_COUNT_FOR_SERVER_CATCHES_FOR_CREATURE_BY_CREATURE_ID = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id = ?;"""

TGOMMO_GET_TOTAL_CATCHES_BY_USER_ID = """SELECT COUNT(*) FROM tgommo_user_creature WHERE user_id = ?;"""
TGOMMO_GET_RARITY_FOR_CREATURE_BY_CREATURE_ID_AND_ENVIRONMENT_ID = """select spawn_rarity from tgommo_environment_creature where creature_id = ? and environment_id = ?;"""
TGOMMO_GET_RARITY_FOR_CREATURE_BY_CREATURE_ID_AND_ENVIRONMENT_DEX_NO = """SELECT spawn_rarity FROM tgommo_environment_creature ec LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id where ec.creature_id = ? and e.dex_no = ?;"""
TGOMMO_GET_RARITY_FOR_CREATURE_BY_CREATURE_ID_AND_DEX_NO = """select spawn_rarity from tgommo_environment_creature where creature_id = ? and environment_id = ?;"""
TGOMMO_GET_IDS_FOR_UNIQUE_CREATURES = """select creature_id from tgommo_creature where variant_no = 1;"""
TGOMMO_GET_IDS_FOR_UNIQUE_CREATURES_IN_ENVIRONMENT = """select ec.creature_id from tgommo_environment_creature ec join tgommo_creature c WHERE c.creature_id = ec.creature_id and ec.environment_id = ? and c.variant_no = 1;"""
TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_USER_BY_ID = """SELECT COUNT(*), COUNT(DISTINCT creature_id) FROM tgommo_user_creature WHERE user_id =? and is_mythical=?;"""
TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_SERVER_BY_ID = """SELECT COUNT(*), COUNT(DISTINCT creature_id) FROM tgommo_user_creature where is_mythical=?;"""
TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_USER_BY_DEX_NUM = """SELECT COUNT(*), COUNT(DISTINCT c.dex_no) FROM tgommo_user_creature uc JOIN tgommo_creature c ON uc.creature_id  = c.creature_id WHERE uc.user_id = ?  and uc.is_mythical=?;"""
TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_SERVER_BY_DEX_NUM = """SELECT COUNT(*), COUNT(DISTINCT c.dex_no) FROM tgommo_user_creature uc JOIN tgommo_creature c ON uc.creature_id  = c.creature_id WHERE uc.is_mythical=?;"""

TGOMMO_GET_ENCYCLOPEDIA_PAGE_DISTINCT_CREATURE_CATCHES_FOR_USER_BASE = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id LEFT JOIN tgommo_creature c ON c.creature_id  = uc.creature_id  WHERE user_id =? AND uc.is_mythical=? AND e.dex_no =?"""
TGOMMO_GET_ENCYCLOPEDIA_PAGE_DISTINCT_CREATURE_CATCHES_FOR_SERVER_BASE = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id LEFT JOIN tgommo_creature c ON c.creature_id  = uc.creature_id  WHERE uc.is_mythical=? AND e.dex_no =?"""
TGOMMO_GET_MAX_VARIANT_NUMBER_FOR_CREATURES = """SELECT COUNT(DISTINCT(variant_no)) FROM tgommo_creature"""


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

'''============='''
'''UPDATE QUERIES'''
'''============='''

TGOMMO_UPDATE_CREATURE_NICKNAME_BY_CATCH_ID = """UPDATE tgommo_user_creature SET nickname = ? WHERE catch_id = ?;"""

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


'''============='''
'''INSERT QUERIES'''
'''============='''

TGOMMO_INSERT_NEW_USER_PROFILE = """INSERT OR IGNORE INTO tgommo_user_profile (user_id, nickname, avatar_id, background_id, creature_slot_id_1, creature_slot_id_2, creature_slot_id_3, creature_slot_id_4, creature_slot_id_5, creature_slot_id_6, currency, available_catch_attempts, rod_level, rod_amount, trap_level, trap_amount) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_NEW_USER_AVATAR = """INSERT OR IGNORE INTO user_avatar (avatar_num, avatar_id, avatar_name, avatar_type, img_root, series, is_parent_entry) VALUES(?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_NEW_AVATAR_UNLOCK_CONDITION = """INSERT OR IGNORE INTO tgommo_user_avatar_unlock_condition (avatar_id, unlock_query, unlock_threshold, is_secret) VALUES(?, ?, ?, ?);"""
TGOMMO_INSERT_NEW_USER_AVATAR_LINK = """INSERT OR IGNORE INTO tgommo_user_profile_avatar_link (avatar_id, user_id) VALUES(?, ?);"""

TGOMMO_INSERT_NEW_ENVIRONMENT = """INSERT OR IGNORE INTO tgommo_environment (environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

TGOMMO_INSERT_NEW_CREATURE = """INSERT OR IGNORE INTO tgommo_creature (creature_id, name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate, default_rarity) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_ENVIRONMENT_CREATURE = """INSERT OR IGNORE INTO tgommo_environment_creature (creature_id, environment_id, spawn_time, creature_name, environment_name, spawn_rarity, local_name, sub_environment_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_USER_CREATURE = """INSERT INTO tgommo_user_creature(user_id, creature_id, creature_variant_no, environment_id, is_mythical, catch_date, nickname) VALUES(?, ?, ?, ?, ?, CURRENT_TIMESTAMP, '') RETURNING catch_id;"""

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

