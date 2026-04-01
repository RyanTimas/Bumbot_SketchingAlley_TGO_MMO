# COLLECTION QUEST QUERIES
TGOMMO_GET_USERS_WHO_PLAYED_IN_TIMERANGE = """SELECT DISTINCT user_id FROM tgommo_user_creature WHERE catch_date > ? AND  catch_date < ?;"""

'''GENERIC QUEST QUERIES'''
AVATAR_VARIANTS_QUEST_1_QUERY = """SELECT COUNT(DISTINCT(c.creature_id)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.variant_no != 1 AND uc.user_id = ?;"""
AVATAR_MYTHICAL_QUEST_QUERY = """SELECT COUNT(DISTINCT(creature_id)) FROM tgommo_user_creature WHERE is_mythical = 1 AND user_id = ?;"""
AVATAR_LEGENDARY_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.dex_no)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id WHERE ec.spawn_rarity = 'Legendary' AND uc.user_id = ?;"""
AVATAR_EPIC_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.dex_no)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id WHERE ec.spawn_rarity = 'Epic' AND uc.user_id = ?;"""

AVATAR_TOTAL_MYTHICAL_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE is_mythical = 1 AND user_id = ?;"""
AVATAR_TOTAL_LEGENDARY_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id WHERE ec.spawn_rarity = 'Legendary' AND uc.user_id = ?;"""
AVATAR_TOTAL_EPIC_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id WHERE ec.spawn_rarity = 'Epic' AND uc.user_id = ?;"""

AVATAR_TOTAL_UNIQUE_CREATURES_CAUGHT_QUERY = """SELECT COUNT(DISTINCT(c.dex_no)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id WHERE uc.user_id = ?;"""
# region ENVIRONMENT QUEST QUERIES
AVATAR_TOTAL_EST_US_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature uc LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id WHERE e.dex_no = 1 AND uc.user_id = ?;"""
AVATAR_TOTAL_FL_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature uc LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id WHERE e.dex_no = 2 AND uc.user_id = ?;"""

AVATAR_DISTINCT_EST_US_QUERY = """SELECT COUNT(DISTINCT(c.dex_no)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id WHERE e.dex_no = 1 AND uc.user_id = ?;"""
AVATAR_DISTINCT_FL_QUERY = """SELECT COUNT(DISTINCT(c.dex_no)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id LEFT JOIN tgommo_environment_creature ec ON uc.creature_id = ec.creature_id LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id WHERE e.dex_no = 2 AND uc.user_id = ?;"""
# endregion

# region KINGDOM QUEST QUERIES
AVATAR_TOTAL_MAMMAL_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Mammal"  AND uc.user_id = ?;"""
AVATAR_TOTAL_BIRD_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Bird"  AND uc.user_id = ?;"""
AVATAR_TOTAL_REPTILE_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Reptile"  AND uc.user_id = ?;"""
AVATAR_TOTAL_AMPHIBIAN_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Amphibian"  AND uc.user_id = ?;"""
AVATAR_TOTAL_INSECT_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Insect"  AND uc.user_id = ?;"""
AVATAR_TOTAL_BUG_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom IN ("Insect", "Arachnid")  AND uc.user_id = ?;"""
AVATAR_TOTAL_CRUSTACEAN_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Crustacean"  AND uc.user_id = ?;"""

AVATAR_DISTINCT_MAMMAL_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.dex_no)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Mammal"  AND uc.user_id = ?;"""
AVATAR_DISTINCT_BIRD_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.dex_no)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Bird"  AND uc.user_id = ?;"""
AVATAR_DISTINCT_REPTILE_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.dex_no)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Reptile"  AND uc.user_id = ?;"""
AVATAR_DISTINCT_AMPHIBIAN_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.dex_no)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Amphibian"  AND uc.user_id = ?;"""
AVATAR_DISTINCT_BUG_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.dex_no)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom IN ("Insect", "Arachnid")  AND uc.user_id = ?;"""
AVATAR_DISTINCT_CRUSTACEAN_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.dex_no)) FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Crustacean"  AND uc.user_id = ?;"""
# endregion
# region ANIMAL TYPE QUEST QUERIES
AVATAR_CANINES_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (27, 32, 59, 169, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 245)  AND user_id = ?;"""
AVATAR_FELINES_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (28, 33, 34, 35, 36, 60)  AND user_id = ?;"""
AVTAR_SQUIRRELS_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (3, 5, 56, 66, 67, 167)  AND user_id = ?;"""
AVATAR_DEER_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (1, 2, 30, 31, 243, 244)  AND user_id = ?;"""

AVATAR_BIRDS_OF_PRAY_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (25, 50, 140)  AND user_id = ?;"""

AVATAR_SNAKES_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (18, 128, 129, 190)  AND user_id = ?;"""
AVATAR_CROCODILIANS_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (120, 185)  AND user_id = ?;"""

AVATAR_SPIDERS_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (46, 162, 163)  AND user_id = ?;"""

# endregion

'''SPECIFIC QUEST QUERIES'''
# COLLECTION QUEST QUERIES
# INDIVIDUAL QUEST QUERIES
# WAVE 2
AVATAR_TURBOGRANNY_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (3, 56)  AND user_id = ?;"""
AVATAR_MORDECAI_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (10)  AND user_id = ?;"""
AVATAR_RIGBY_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (6)  AND user_id = ?;"""
# WAVE 3
AVATAR_BUGS_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (4)  AND user_id = ?;"""
AVATAR_DAFFY_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (21,22)  AND user_id = ?;"""
AVATAR_BUBSY_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (28)  AND user_id = ?;"""
AVATAR_MARCELINE_QUEST_QUERY =  """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (55)  AND user_id = ?;"""
# WAVE 4
AVATAR_MICKEY_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (37)  AND user_id = ?;"""
AVATAR_BEETLEJUICE_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (115,116,226)  AND user_id = ?;"""
AVATAR_FOX_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (27,169)  AND user_id = ?;"""
AVATAR_BUCK_BUMBLE_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (91, 221)  AND user_id = ?;"""
AVATAR_MISS_PIGGY_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (69)  AND user_id = ?;"""
AVATAR_SNOOPY_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (207)  AND user_id = ?;"""
AVATAR_MARMADUKE_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (210)  AND user_id = ?;"""
AVATAR_DWAYNE_LAFONTANT_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (26, 57, 58, 19, 48, 102, 126, 127, 181)  AND user_id = ?;"""
AVATAR_MARCUS_QUEST_QUERY = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id IN (63)  AND user_id = ?;"""

# TRANSCENDANT QUEST QUERIES
AVATAR_BIGFOOT_QUEST_QUERY = """SELECT COUNT(*) >= 1 FROM tgommo_user_creature WHERE creature_id = 9001 AND user_id = ?;"""
AVATAR_MOTHMAN_QUEST_QUERY = """SELECT COUNT(*) >= 1 FROM tgommo_user_creature WHERE creature_id = 9002 AND user_id = ?;"""
AVATAR_FROGMAN_QUEST_QUERY = """SELECT COUNT(*) >= 1 FROM tgommo_user_creature WHERE creature_id = 9003 AND user_id = ?;"""
AVATAR_SKUNK_APE_QUEST_QUERY = """SELECT COUNT(*) >= 1 FROM tgommo_user_creature WHERE creature_id = 9004 AND user_id = ?;"""


''' ----- COLLECTION QUEST QUERIES ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
# region COLLECTION QUEST QUERIES
TGOMMO_COLLECTION_QUERY_ALL_CREATURES_TOTAL = """SELECT COUNT(DISTINCT ec.creature_id) FROM tgommo_environment_creature ec LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id ;"""
TGOMMO_COLLECTION_QUERY_ALL_CREATURES_CAUGHT = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_environment e ON uc.environment_id = e.environment_id WHERE user_id=?;"""

TGOMMO_COLLECTION_QUERY_US_EAST_TOTAL = """SELECT COUNT(DISTINCT ec.creature_id) FROM tgommo_environment_creature ec LEFT JOIN tgommo_environment e ON ec.environment_id = e.environment_id WHERE e.dex_no =1;"""
TGOMMO_COLLECTION_QUERY_US_EAST_CAUGHT = """SELECT COUNT(DISTINCT uc.creature_id) FROM tgommo_user_creature uc LEFT JOIN tgommo_environment e ON uc.environment_id = e.environment_id WHERE e.dex_no =1 AND user_id=?;"""

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
# endregion