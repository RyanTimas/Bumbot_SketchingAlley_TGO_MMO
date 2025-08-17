import sqlite3

from src.resources.db_queries import SA_CREATE_DELUXEWALLENTRIES_TABLE, SA_CREATE_ROLES_TABLE, SA_CREATE_USERS_TABLE


class QueryHandler:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.init_tables()

    def connect_to_db(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def close_db(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None
            self.cursor = None

    def init_tables(self):
        self.execute_query(SA_CREATE_DELUXEWALLENTRIES_TABLE)
        self.execute_query(SA_CREATE_USERS_TABLE)
        self.execute_query(SA_CREATE_ROLES_TABLE)

    def execute_query(self, query, params=None):
        self.connect_to_db()

        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

        return_value = self.cursor.fetchall() if query.strip().upper().startswith("SELECT") else self.conn.commit()
        self.close_db()

        return return_value


    def get_conn(self):
        return self.conn

    def get_cursor(self):
        return self.cursor