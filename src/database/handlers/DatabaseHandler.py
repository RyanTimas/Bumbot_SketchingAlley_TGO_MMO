from src.database.handlers.TGOMMODatabaseInitializer import TGOMMODatabaseInitializer
from src.database.handlers.TGOMMO_DatabaseHandler import TGOMMODatabaseHandler
from src.database.handlers.User_DatabaseHandler import UserDatabaseHandler
from src.resources.constants.general_constants import DISCORD_DATABASE, RUN_TGOMMO_DB_INIT

# Global instance - initialized as None
_db_handler = None
_tgommo_db_handler = None
_user_db_handler = None

def initialize_database():
    """Initialize the global database handler instance"""
    global _db_handler, _user_db_handler, _tgommo_db_handler

    _db_handler = DatabaseHandler(DISCORD_DATABASE)

    _user_db_handler = _db_handler.user_database_handler
    _tgommo_db_handler = _db_handler.tgommo_database_handler
    return _db_handler


def get_db_handler():
    """Get the global database handler instance"""
    global _db_handler
    if _db_handler is None:
        raise RuntimeError("Database handler not initialized. Call initialize_database() first.")
    return _db_handler


def get_tgommo_db_handler() -> TGOMMODatabaseHandler:
    global _tgommo_db_handler
    if _tgommo_db_handler is None:
        raise RuntimeError("Database handler not initialized. Call initialize_database() first.")
    return _tgommo_db_handler


def get_user_db_handler() -> UserDatabaseHandler:
    global _user_db_handler
    if _user_db_handler is None:
        raise RuntimeError("Database handler not initialized. Call initialize_database() first.")
    return _user_db_handler


class DatabaseHandler:
    def __init__(self, db_file):
        self.user_database_handler = UserDatabaseHandler(db_file=db_file)
        self.tgommo_database_handler = TGOMMODatabaseHandler(db_file=db_file)
        self.tgommo_database_initializer = TGOMMODatabaseInitializer(db_handler = self.tgommo_database_handler)

        if RUN_TGOMMO_DB_INIT:
            self.tgommo_database_initializer.initialize_tgommo_database()