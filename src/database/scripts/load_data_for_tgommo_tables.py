import sqlite3

conn = sqlite3.connect('C:/Users/Ryan/PycharmProjects/3rdParty/bumbot.db')

c = conn.cursor()  # cursor

# ----------------
# CREATURE RECORDS
# ----------------

# 01 - Deer
c.execute("""
    INSERT INTO tgommo_creature
    (name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate)
    VALUES
    ('Deer', 'Doe', 1, 1, 'White-Tailed Deer', 'Odocoileus virginianus', 'Mammal', '', 'Deer', 5);)""")
conn.commit()
c.execute("""
    INSERT INTO tgommo_creature
    (name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate)
    VALUES
    ('Deer', 'Buck', 1, 2, 'White-Tailed Deer', 'Odocoileus virginianus', 'Mammal', '', 'Deer', 5);)""")
conn.commit()

# 02 - Squirrel
c.execute("""
    INSERT INTO tgommo_creature
    (name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate)
    VALUES
    ('Squirrel', '', 2, 1, 'Eastern Gray Squirrel', 'Sciurus carolinensis', 'Mammal', '', 'Squirrel', 15);)""")
conn.commit()

# 02 - Rabbit
c.execute("""
    INSERT INTO tgommo_creature
    (name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate)
    VALUES
    ('Rabbit', '', 3, 1, 'Eastern Cottontail', 'Sylvilagus floridanus', 'Mammal', '', 'Rabbit', 10);)""")
conn.commit()

# 04 - Chipmunk
c.execute("""
    INSERT INTO tgommo_creature
    (name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate)
    VALUES
    ('Chipmunk', '', 4, 1, 'Eastern Chipmunk', 'Tamias striatus', 'Mammal', '', 'Chipmunk', 10);)""")
conn.commit()

# 05 - Raccoon
c.execute("""
    INSERT INTO tgommo_creature
    (name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate)
    VALUES
    ('Bear', '', 23, 1, 'Black Bear', 'Ursus americanus', 'Mammal', '', 'Raccoon', 10);)""")
conn.commit()


# 23 - Bear
c.execute("""
    INSERT INTO tgommo_creature
    (name, variant_name, dex_no, variant_no, full_name, scientific_name, kingdom, description, img_root, encounter_rate)
    VALUES
    ('Raccoon', '', 5, 1, 'Raccoon', 'Procyon lotor', 'Mammal', '', 'Raccoon', 10);
)""")
conn.commit()

# -------------------
# ENVIRONMENT RECORDS
# -------------------

# 01 - Eastern United States Forest
c.execute("""
    INSERT INTO tgommo_environment
    (name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate)
    VALUES
    ('Forest', 'Summer - Day', 1, 1, 'Eastern United States', '', 'forest_est', False, True, 5);
)""")
conn.commit()
c.execute("""
    INSERT INTO tgommo_environment
    (name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate)
    VALUES
    ('Forest', 'Summer - Night', 1, 2, 'Eastern United States', '', 'forest_est', True, True, 5);
)""")
conn.commit()
c.execute("""
    INSERT INTO tgommo_environment
    (name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate)
    VALUES
    ('Forest', 'Winter - Day', 1, 2, 'Eastern United States', '', 'forest_est', False, False, 5);
)""")
conn.commit()
c.execute("""
    INSERT INTO tgommo_environment
    (name, variant_name, dex_no, variant_no, location, description, img_root, is_night_environment, in_circulation, encounter_rate)
    VALUES
    ('Forest', 'Winter - Night', 1, 2, 'Eastern United States', '', 'forest_est', False, False, 5);
)""")


conn.commit()
conn.close()