import sqlite3

conn = sqlite3.connect('C:/Users/Ryan/PycharmProjects/3rdParty/bumbot.db')

c = conn.cursor()  # cursor

# create deluxe wall table
    # deluxe_wall_entries table
    # message_id: Unique identifier for the wall entry (Discord message ID)
    # author: Username of the message author
    # author_id: Discord user ID of the author
    # message_text: Content of the wall entry
    # on_deluxe_wall: Status flag (e.g., 'yes'/'no') indicating if entry is on the deluxe wall
    # reaction_amounts: Number of reactions the entry received
    # date: Date the entry was posted
c.execute("""CREATE TABLE IF NOT EXISTS deluxe_wall_entries (
            message_id INTEGER PRIMARY KEY,
            author TEXT,
            author_id INTEGER,
            message_text TEXT,
            on_deluxe_wall TEXT,
            reaction_amounts INTEGER,
            date DATE
        )""")

# users table
    # user_id: Unique identifier for the user (Discord user ID)
    # user_name: Username of the user
    # total_xp: Total experience points accumulated by the user
    # level: User's current level
    # guts: User's 'guts' stat value
    # hearts: User's 'hearts' stat value
    # smarts: User's 'smarts' stat value
    # will: User's 'will' stat value
c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            user_name TEXT,
            total_xp INTEGER,
            level INTEGER,
            guts INTEGER,
            hearts INTEGER,
            smarts INTEGER,
            will INTEGER
        )""")

# roles table
    # role_id: Unique identifier for the role
    # role_name: Name of the role
    # bonus_guts: Bonus 'guts' stat provided by the role
    # bonus_hearts: Bonus 'hearts' stat provided by the role
    # bonus_smarts: Bonus 'smarts' stat provided by the role
    # bonus_will: Bonus 'will' stat provided by the role
    # bonus_move_id: ID of the bonus move associated with the role
c.execute("""CREATE TABLE IF NOT EXISTS roles (
            role_id INTEGER PRIMARY KEY,
            role_name TEXT,
            bonus_guts INTEGER,
            bonus_hearts INTEGER,
            bonus_smarts INTEGER,
            bonus_will INTEGER,
            bonus_move_id INTEGER
        )""")





#==============================================================
#TGO MMO TABLES
#==============================================================

# creatures table
    # creature_id: Unique identifier for the creature
    # name: Short name of the creature
    # variant_name: Name of the variant (if applicable)

    # dex_no: Creature's Pokédex-style number
    # variant_no: Variant number for alternate forms

    # full_name: Full name of the creature
    # scientific_name: Scientific name of the creature
    # kingdom: Biological kingdom classification
    # description: Description of the creature

    # img_root: root for filenames when referencing this environment
    # encounter_rate: Rarity rating of the creature
c.execute("""CREATE TABLE IF NOT EXISTS tgommo_creature (
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
            encounter_rate INTEGER NOT NULL
        )""")


# environments table
    # environment_id: Unique identifier for the environment
    # name: Name of the environment
    # variant_name: Variant name of the environment (if applicable)

    # location: real life location for the environment
    # description: Description of the environment

    # img_root: root for filenames when referencing this environment
    # encounter_rate: Rarity rating of the environment (if applicable)
    # is_night_environment: signifies if this environment is a nighttime variant or not
c.execute("""CREATE TABLE IF NOT EXISTS tgommo_environment (
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
            encounter_rate INTEGER NOT NULL
        )""")


#*************************************************************
#JUNCTION TABLES
#*************************************************************

# Create environment_creature junction table
    # creature_id: Foreign key to creatures table
    # environment_id: Foreign key to environments table

    # spawn_rarity: The rarity of this creature in this specific environment
    # local_name: Name for the creature specific to this environment (if applicable)
c.execute("""CREATE TABLE IF NOT EXISTS tgommo_environment_creature (
    creature_id INTEGER  NOT NULL,
    environment_id INTEGER NOT NULL,
    
    spawn_rarity TEXT NOT NULL,
    local_name TEXT DEFAULT '',
    
    PRIMARY KEY (creature_id, environment_id),
    FOREIGN KEY (creature_id) REFERENCES tgommo_creature (creature_id),
    FOREIGN KEY (environment_id) REFERENCES tgommo_environment (environment_id)
)""")


# Create user_creature junction table - records which user has caught which creature, where and when
    # catch_id: Unique autoincrement identifier for each catch (primary key)

    # user_id: Foreign key to users table (the user who caught the creature)
    # creature_id: Foreign key to creatures table (the creature that was caught)
    # creature_variant_no: Foreign key to creatures table (the creature that was caught)
    # environment_id: Foreign key to environments table (where the creature was caught)

    # is_mythical: signifies if the caught creature is a mythical creature
    # catch_date: Timestamp when the creature was caught
    # nickname: Optional nickname given to the creature by the user
c.execute("""CREATE TABLE IF NOT EXISTS tgommo_user_creature (
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
)""")

# todo: add a table to keep track of user TGO MMO profiles, which track items, currencies, total catches, etc.

conn.commit()
conn.close()