# COLLECTION QUEST QUERIES
AVATAR_DONKEY_KONG_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.creature_id)) >= 20 FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Mammal"  AND uc.user_id = ?;"""
AVATAR_BIG_BIRD_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.creature_id)) >= 18 FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Bird"  AND uc.user_id = ?;"""
AVATAR_GEX_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.creature_id)) >= 3 FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Reptile"  AND uc.user_id = ?;"""
AVATAR_KERMIT_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.creature_id))  >= 2 FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom = "Amphibian"  AND uc.user_id = ?;"""
AVATAR_HORNET_QUEST_QUERY = """SELECT COUNT(DISTINCT(c.creature_id))  >= 7 FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.kingdom IN ("Insect", "Arachnid")  AND uc.user_id = ?;"""

AVATAR_VARIANTS_QUEST_1_QUERY = """SELECT COUNT(DISTINCT(c.creature_id)) >= 10 FROM tgommo_user_creature uc LEFT JOIN tgommo_creature c ON uc.creature_id = c.creature_id WHERE c.variant_no != 1 AND uc.user_id = ?;"""
AVATAR_MYTHICAL_QUEST_1_QUERY = """SELECT COUNT(DISTINCT(creature_id)) >= 1 FROM tgommo_user_creature WHERE is_mythical = 1 AND user_id = ?;"""
AVATAR_MYTHICAL_QUEST_2_QUERY = """SELECT COUNT(DISTINCT(creature_id)) >= 5 FROM tgommo_user_creature WHERE is_mythical = 1 AND user_id = ?;"""

# INDIVIDUAL QUEST QUERIES
AVATAR_SQUIRRELGIRL_QUEST_QUERY = """SELECT COUNT(*) >= 100 FROM tgommo_user_creature WHERE creature_id IN (3, 56)  AND user_id = ?;"""

# TRANSCENDANT QUEST QUERIES
AVATAR_BIGFOOT_QUEST_QUERY = """SELECT COUNT(*) >= 1 FROM tgommo_user_creature WHERE creature_id = 9001 AND user_id = ?;"""
AVATAR_MOTHMAN_QUEST_QUERY = """SELECT COUNT(*) >= 1 FROM tgommo_user_creature WHERE creature_id = 9002 AND user_id = ?;"""
AVATAR_FROGMAN_QUEST_QUERY = """SELECT COUNT(*) >= 1 FROM tgommo_user_creature WHERE creature_id = 9003 AND user_id = ?;"""
