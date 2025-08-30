'''**********************'''
'''Table Creation Queries'''
'''**********************'''
SA_CREATE_DELUXEWALLENTRIES_TABLE = "CREATE TABLE IF NOT EXISTS deluxe_wall_entries (\n" \
    "    message_id INTEGER PRIMARY KEY,\n" \
    "    author TEXT,\n" \
    "    author_id INTEGER,\n" \
    "    message_text TEXT,\n" \
    "    on_deluxe_wall TEXT,\n" \
    "    reaction_amounts INTEGER,\n" \
    "    date DATE\n" \
    ")"
SA_CREATE_USERS_TABLE = "CREATE TABLE IF NOT EXISTS users (\n" \
    "    user_id INTEGER PRIMARY KEY,\n" \
    "    user_name TEXT,\n" \
    "    total_xp INTEGER,\n" \
    "    level INTEGER,\n" \
    "    guts INTEGER,\n" \
    "    hearts INTEGER,\n" \
    "    smarts INTEGER,\n" \
    "    will INTEGER\n" \
    ")"
SA_CREATE_ROLES_TABLE = "CREATE TABLE IF NOT EXISTS roles (\n" \
    "    role_id INTEGER PRIMARY KEY,\n" \
    "    role_name TEXT,\n" \
    "    bonus_guts INTEGER,\n" \
    "    bonus_hearts INTEGER,\n" \
    "    bonus_smarts INTEGER,\n" \
    "    bonus_will INTEGER,\n" \
    "    bonus_move_id INTEGER\n" \
    ")"

TGOMMO_CREATE_CREATURE_TABLE = """CREATE TABLE IF NOT EXISTS tgommo_creature (
            creature_id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            name TEXT NOT NULL,
            variant_name TEXT DEFAULT '',
            dex_no INTEGER NOT NULL,
            variant_no INTEGER NOT NULL,
            
            full_name TEXT NOT NULL,
            scientific_name TEXT NOT NULL,
            kingdom TEXT NOT NULL,
            description TEXT DEFAULT '',
            
            img_root TEXT NOT NULL,
            encounter_rate INTEGER NOT NULL,
            UNIQUE(dex_no, variant_no)
        )"""
TGOMMO_CREATE_ENVIRONMENT_TABLE = """CREATE TABLE IF NOT EXISTS tgommo_environment (
            environment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            name TEXT NOT NULL,
            variant_name TEXT DEFAULT '',

            dex_no INTEGER NOT NULL,
            variant_no INTEGER NOT NULL,
            
            location TEXT NOT NULL,
            description TEXT DEFAULT '',
            
            img_root TEXT NOT NULL,
            is_night_environment BOOLEAN NOT NULL,
            in_circulation BOOLEAN NOT NULL,
            encounter_rate INTEGER NOT NULL,
            UNIQUE(dex_no, variant_no)
        )"""
TGOMMO_CREATE_ENVIRONMENT_CREATURE_TABLE = """CREATE TABLE IF NOT EXISTS tgommo_environment_creature (
    creature_id INTEGER NOT NULL,
    environment_id INTEGER NOT NULL,
    creature_name TEXT NOT NULL,
    environment_name TEXT NOT NULL,
    
    spawn_rarity TEXT NOT NULL,
    local_name TEXT DEFAULT '',
    
    UNIQUE(creature_id, environment_id),

    PRIMARY KEY (creature_id, environment_id),
    FOREIGN KEY (creature_id, creature_name) REFERENCES tgommo_creature (creature_id, name),
    FOREIGN KEY (environment_id, environment_name) REFERENCES tgommo_environment (environment_id, name)
)"""
TGOMMO_CREATE_USER_CREATURE_TABLE = """CREATE TABLE IF NOT EXISTS tgommo_user_creature (
    catch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    user_id INTEGER,
    creature_id INTEGER,
    creature_variant_no INTEGER,
    environment_id INTEGER,

    is_mythical BOOLEAN DEFAULT 0,
    catch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nickname TEXT DEFAULT '',
    
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (creature_id) REFERENCES tgommo_creature (creature_id),
    FOREIGN KEY (creature_variant_no) REFERENCES tgommo_creature (creature_id),
    FOREIGN KEY (environment_id) REFERENCES tgommo_environment (environment_id)
)"""

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
''' TGO MMO Queries   '''
'''*******************'''
TGOMMO_INSERT_NEW_CREATURE = """INSERT OR IGNORE INTO tgommo_creature (name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_NEW_ENVIRONMENT = """INSERT OR IGNORE INTO tgommo_environment (name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_ENVIRONMENT_CREATURE = """INSERT OR IGNORE INTO tgommo_environment_creature (creature_id, environment_id, creature_name, environment_name, spawn_rarity, local_name) VALUES(?, ?, ?, ?, ?, ?);"""
TGOMMO_INSERT_USER_CREATURE = """INSERT INTO tgommo_user_creature(user_id, creature_id, creature_variant_no, environment_id, is_mythical, catch_date, nickname) VALUES(?, ?, ?, ?, ?, CURRENT_TIMESTAMP, '');"""

TGOMMO_SELECT_CREATURE_BY_ID = """SELECT creature_id, name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate FROM tgommo_creature WHERE creature_id = ?"""
TGOMMO_SELECT_ENVIRONMENT_BY_ID = """SELECT environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate FROM tgommo_environment WHERE environment_id = ?"""

TGOMMO_SELECT_CREATURE_BY_DEX_AND_VARIANT_NUMBER = """SELECT creature_id, name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate FROM tgommo_creature WHERE dex_no = ? AND variant_no = ?"""
TGOMMO_SELECT_ENVIRONMENT_BY_DEX_AND_VARIANT_NUMBER = """SELECT environment_id, name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate FROM tgommo_environment WHERE dex_no = ? AND variant_no = ?"""
TGOMMO_SELECT_CREATURES_FROM_SPECIFIED_ENVIRONMENT = """SELECT c.dex_no, c.variant_no, ce.local_name, ce.spawn_rarity FROM tgommo_creature c JOIN tgommo_environment_creature ce ON c.creature_id = ce.creature_id WHERE ce.environment_id = ?"""
TGOMMO_SELECT_RANDOM_ENVIRONMENT_ID = """SELECT environment_id FROM environments ORDER BY RANDOM() LIMIT 1"""

TGOMMO_SELECT_CREATURE_ID_BY_DEX_AND_VARIANT_NO = """SELECT creature_id, name FROM tgommo_creature WHERE dex_no = ? AND variant_no = ?"""
TGOMMO_SELECT_ENVIRONMENT_ID_BY_DEX_AND_VARIANT_NO = """SELECT environment_id, name FROM tgommo_environment WHERE dex_no = ? AND variant_no = ?"""
TGOMMO_SELECT_ALL_CREATURES_CAUGHT_BY_USER = """SELECT c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no, COUNT(uc.creature_id) as total_catches, SUM(CASE WHEN uc.is_mythical = 1 THEN 1 ELSE 0 END) as mythical_catches FROM tgommo_creature c LEFT JOIN tgommo_user_creature uc ON c.creature_id = uc.creature_id AND uc.user_id = ? GROUP BY c.creature_id, c.name, c.variant_name, c.dex_no, c.variant_no ORDER BY c.dex_no, c.variant_no;"""

TGOMMO_GET_COUNT_FOR_USER_CATCHES_FOR_CREATURE_BY_DEX_NUM = """SELECT COUNT(*) FROM tgommo_user_creature uc JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE uc.user_id = ? AND c.dex_no = ?;"""
TGOMMO_GET_COUNT_FOR_USER_CATCHES_FOR_CREATURE_BY_DEX_NUM_AND_VARIANT_NUM = """SELECT COUNT(*) FROM tgommo_user_creature uc JOIN tgommo_creature c ON c.creature_id = uc.creature_id WHERE uc.user_id = ? AND c.dex_no = ? AND c.variant_no = ?;"""
TGOMMO_GET_COUNT_FOR_SERVER_CATCHES_FOR_CREATURE_BY_CREATURE_ID = """SELECT COUNT(*) FROM tgommo_user_creature WHERE creature_id = ?;"""
TGOMMO_GET_TOTAL_CATCHES_BY_USER_ID = """SELECT COUNT(*) FROM tgommo_user_creature WHERE user_id = ?;"""
TGOMMO_GET_RARITY_FOR_CREATURE_BY_CREATURE_ID_AND_ENVIRONMENT_ID = """select spawn_rarity from tgommo_environment_creature where creature_id = ? and environment_id = ?;"""
TGOMMO_GET_IDS_FOR_UNIQUE_CREATURES = """select creature_id from tgommo_creature where variant_no = 1;"""
TGOMMO_GET_IDS_FOR_UNIQUE_CREATURES_IN_ENVIRONMENT = """select ec.creature_id from tgommo_environment_creature ec join tgommo_creature c WHERE c.creature_id = ec.creature_id and ec.environment_id = ? and c.variant_no = 1;"""
TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_USER = """SELECT COUNT(*), COUNT(DISTINCT creature_id) FROM tgommo_user_creature WHERE user_id =?;"""
TGOMMO_GET_ENCYCLOPEDIA_PAGE_INFO_FOR_SERVER = """SELECT COUNT(*), COUNT(DISTINCT creature_id) FROM tgommo_user_creature;"""
