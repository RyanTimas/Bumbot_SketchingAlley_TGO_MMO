'''**********************'''
'''Table Creation Queries'''
'''**********************'''
'''GENERAL TABLES'''
SA_CREATE_DELUXEWALLENTRIES_TABLE = """CREATE TABLE IF NOT EXISTS deluxe_wall_entries (
    message_id INTEGER PRIMARY KEY,
    author TEXT,
    author_id INTEGER,
    message_text TEXT,
    on_deluxe_wall TEXT,
    reaction_amounts INTEGER,
    date DATE
)"""
SA_CREATE_USERS_TABLE = """CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    user_name TEXT,
    total_xp INTEGER,
    level INTEGER,
    guts INTEGER,
    hearts INTEGER,
    smarts INTEGER,
    will INTEGER
)"""
TGOMMO_CREATE_AVATAR_TABLE = """CREATE TABLE IF NOT EXISTS user_avatar (
    avatar_num INTEGER PRIMARY KEY AUTOINCREMENT,
    avatar_id TEXT UNIQUE,
    avatar_name TEXT NOT NULL,
    avatar_type TEXT NOT NULL,
    img_root TEXT NOT NULL,
    series TEXT,
    is_parent_entry BOOLEAN DEFAULT False,
    UNIQUE(avatar_id)
)"""
SA_CREATE_ROLES_TABLE = """CREATE TABLE IF NOT EXISTS roles (
    role_id INTEGER PRIMARY KEY,
    role_name TEXT,
    bonus_guts INTEGER,
    bonus_hearts INTEGER,
    bonus_smarts INTEGER,
    bonus_will INTEGER,
    bonus_move_id INTEGER
)"""

'''TGO MMO TABLES'''
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
    spawn_time string NOT NULL,

    creature_name TEXT NOT NULL,
    environment_name TEXT NOT NULL,

    spawn_rarity TEXT NOT NULL,
    local_name TEXT DEFAULT '',
    sub_environment_type TEXT DEFAULT '',

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
    
    is_released BOOLEAN DEFAULT 0,
    is_favorite BOOLEAN DEFAULT 0,

    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (creature_id) REFERENCES tgommo_creature (creature_id),
    FOREIGN KEY (creature_variant_no) REFERENCES tgommo_creature (creature_id),
    FOREIGN KEY (environment_id) REFERENCES tgommo_environment (environment_id)
)"""

TGOMMO_CREATE_USER_PROFILE_TABLE = """CREATE TABLE IF NOT EXISTS tgommo_user_profile (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,

    nickname TEXT DEFAULT '',
    avatar_id TEXT DEFAULT "D1",
    background_id INTEGER DEFAULT 1,

    creature_slot_id_1 INTEGER,
    creature_slot_id_2 INTEGER,
    creature_slot_id_3 INTEGER,
    creature_slot_id_4 INTEGER,
    creature_slot_id_5 INTEGER,
    creature_slot_id_6 INTEGER,

    currency INTEGER,
    available_catch_attempts INTEGER DEFAULT 3,
    rod_level INTEGER DEFAULT 1,
    rod_amount INTEGER DEFAULT 0,
    trap_level INTEGER DEFAULT 1,
    trap_amount INTEGER DEFAULT 0,

    UNIQUE(user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)"""
TGOMMO_CREATE_USER_AVATAR_LINK_TABLE = """CREATE TABLE IF NOT EXISTS tgommo_user_profile_avatar_link (
    avatar_id TEXT,
    user_id INTEGER NOT NULL,
    UNIQUE(avatar_id, user_id),
    PRIMARY KEY (avatar_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (avatar_id) REFERENCES user_avatar (avatar_id)
)"""
TGOMMO_CREATE_AVATAR_UNLOCK_CONDITION_TABLE = """CREATE TABLE IF NOT EXISTS tgommo_user_avatar_unlock_condition (
    avatar_id TEXT,
    unlock_query TEXT,
    unlock_threshold INTEGER,
    is_secret BOOLEAN DEFAULT 0,

    PRIMARY KEY (avatar_id),
    FOREIGN KEY (avatar_id) REFERENCES user_avatar (avatar_id)
)"""

TGOMMO_CREATE_COLLECTION_TABLE = """CREATE TABLE IF NOT EXISTS tgommo_collection (
    collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    image_path TEXT NOT NULL,
    background_color_path TEXT NOT NULL,
    total_count_query TEXT NOT NULL,
    caught_count_query TEXT NOT NULL,
    completion_reward_1 TEXT NOT NULL DEFAULT '',
    completion_reward_2 TEXT NOT NULL DEFAULT '',
    completion_reward_3 TEXT NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT 1
)"""
