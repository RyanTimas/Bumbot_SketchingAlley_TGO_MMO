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

'''*******************'''
'''   USER Queries    '''
'''*******************'''
SA_USERS_INSERT_NEW_RECORD = "INSERT INTO users (user_id, user_name, total_xp, level, guts, hearts, smarts, will) VALUES(?, ?, ?, ?, ?, ?, ?, ?);"

SA_USERS_SELECT_ALL = "SELECT * FROM users"
SA_USERS_SELECT_ALL_BY_USERID = "SELECT * FROM users WHERE user_id=?"

SA_USERS_UPDATE_XP = "UPDATE users SET total_xp=? WHERE user_id=?"
SA_USERS_UPDATE_LEVEL = "UPDATE users SET level=? WHERE user_id=?"
SA_USERS_UPDATE_PLAYER_STATS = "UPDATE users SET guts=?, hearts=?,smarts=?,will=? WHERE user_id=?"

SA_USERS_DELETE_BY_USERID = "DELETE FROM users WHERE user_id=?"

'''*******************'''
'''Deluxe Wall Queries'''
'''*******************'''
SA_DELUXEWALLENTRY_INSERT_NEW_RECORD = "INSERT INTO deluxe_wall_entries (message_id, author, author_id, message_text, on_deluxe_wall, reaction_amounts, date) VALUES(?, ?, ?, ?, ?, ?, ?);"

SA_DELUXEWALLENTRY_SELECT_ALL = "SELECT * FROM deluxe_wall_entries;"
SA_DELUXEWALLENTRY_SELECT_BY_MESSAGEID = "SELECT * FROM deluxe_wall_entries WHERE message_id=?;"
SA_DELUXEWALLENTRY_SELECT_ONDELUXWALL_BY_MESSAGEID = "SELECT on_deluxe_wall FROM deluxe_wall_entries WHERE message_id=?;"

SA_DELUXEWALLENTRY_UPDATE_REACTIONAMOUNT = "UPDATE deluxe_wall_entries SET reaction_amounts=? WHERE message_id=?;"
SA_DELUXEWALLENTRY_UPDATE_ONDELUXEWALL = "UPDATE deluxe_wall_entries SET on_deluxe_wall=? WHERE message_id=?;"

SA_DELUXEWALLENTRY_DELETE_BY_MESSAGEID = "DELETE FROM deluxe_wall_entries WHERE message_id=?;"