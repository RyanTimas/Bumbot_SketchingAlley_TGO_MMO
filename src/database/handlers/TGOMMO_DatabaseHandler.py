from xml.dom import UserDataHandler

from src.database.handlers.QueryHandler import QueryHandler
from src.database.handlers.User_DatabaseHandler import UserDatabaseHandler


class TGOMMODatabaseHandler:
    def __init__(self, db_file):
        self.QueryHandler = QueryHandler(db_file=db_file)
