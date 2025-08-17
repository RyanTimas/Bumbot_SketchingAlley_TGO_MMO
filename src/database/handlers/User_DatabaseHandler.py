from src.database.handlers.QueryHandler import QueryHandler
from src.resources.db_queries import SA_USERS_INSERT_NEW_RECORD, SA_USERS_SELECT_ALL, SA_USERS_SELECT_ALL_BY_USERID, \
    SA_USERS_DELETE_BY_USERID, SA_USERS_UPDATE_LEVEL, SA_USERS_UPDATE_XP

from src.discord.objects.User import User


class UserDatabaseHandler:
    def __init__(self, db_file):
        self.QueryHandler = QueryHandler(db_file=db_file)

    def insert_new_record(self, params=(0,'',0,0,0,0,0,0)):
        return self.QueryHandler.execute_query(SA_USERS_INSERT_NEW_RECORD, params=params)

    ''' Deluxe Wall Select Queries '''
    def select_all(self):
        return self.QueryHandler.execute_query(SA_USERS_SELECT_ALL)

    def select_by_user_id(self, user_id=0, user_name=None):
        response = self.QueryHandler.execute_query(SA_USERS_SELECT_ALL_BY_USERID, params=(user_id,))

        if not response:
            self.insert_new_record((user_id, user_name, 0, 0, 0, 0, 0, 0))
            response = self.QueryHandler.execute_query(SA_USERS_SELECT_ALL_BY_USERID, params=(user_id,))

        if response:
            entry = response[0]
            return User(user_id=entry[0], user_name=entry[1], total_xp=entry[2], level=entry[3], guts=entry[4], hearts=entry[5], smarts=entry[6], will=entry[7])
        return response

    ''' Deluxe Wall Update Queries '''
    def update_level(self, params=(0, 0)):
        return self.QueryHandler.execute_query(SA_USERS_UPDATE_LEVEL, params=params)

    def update_xp(self, xp_amount=0, user_id=0, user_name=None):
        current_xp = self.select_by_user_id(user_id=user_id, user_name=user_name).total_xp
        return self.QueryHandler.execute_query(SA_USERS_UPDATE_XP, params=(current_xp + xp_amount, user_id))

    def update_player_stats(self, params=(0,0,0,0)):
        return self.QueryHandler.execute_query(SA_USERS_UPDATE_XP, params=params)

    ''' Deluxe Wall Delete Queries '''
    def delete(self, params=0):
        return self.QueryHandler.execute_query(SA_USERS_DELETE_BY_USERID, params=params)
