from src.database.handlers.TGOMMO_DatabaseHandler import TGOMMODatabaseHandler
from src.database.handlers.User_DatabaseHandler import UserDatabaseHandler


class DatabaseHandler:
    def __init__(self, db_file):
        self.user_database_handler = UserDatabaseHandler(db_file=db_file)
        self.tgommo_database_handler = TGOMMODatabaseHandler(db_file=db_file)