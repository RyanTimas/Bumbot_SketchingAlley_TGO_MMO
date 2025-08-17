import sqlite3

conn = sqlite3.connect('C:/Users/Ryan/PycharmProjects/3rdParty/bumbot.db')

c = conn.cursor()  # cursor

# create deluxe wall table
c.execute("""CREATE TABLE IF NOT EXISTS deluxe_wall_entries (
            message_id INTEGER PRIMARY KEY,
            author TEXT,
            author_id INTEGER,
            message_text TEXT,
            on_deluxe_wall TEXT,
            reaction_amounts INTEGER,
            date DATE
        )""")

# create user table
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

# create roles table
c.execute("""CREATE TABLE IF NOT EXISTS roles (
            role_id INTEGER PRIMARY KEY,
            role_name TEXT,
            bonus_guts INTEGER,
            bonus_hearts INTEGER,
            bonus_smarts INTEGER,
            bonus_will INTEGER,
            bonus_move_id INTEGER
        )""")

# commit
conn.commit()

# close the connection
conn.close()