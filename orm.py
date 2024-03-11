import os
import sqlite3
from datetime import datetime


class SQL(object):
    def __init__(self, name):
        super(SQL, self).__init__()
        self.name = name
        self.path = os.path.join('index')
        self.filename = f'{name}.sqlite'
        self.dest = os.path.join(self.path, self.filename)
        self.__connection = None
        self.__cursor = None
        self.__table = 'data'
        self.__primary_key = 'hsh'

        if not os.path.isdir(self.path):
            os.makedirs(self.path, exist_ok=True)

        self.connect()
        self.create_table()

    def connect(self):
        try:
            self.__connection = sqlite3.connect(self.dest)
            self.__cursor = self.__connection.cursor()
        except Exception:
            raise

    def execute(self, query, param=None):
        try:
            if param is not None:
                self.__cursor.execute(query, param)
            else:
                self.__cursor.execute(query)
        except Exception:
            raise

    def close(self):
        try:
            self.__cursor.close()
        except Exception:
            raise

    def create_table(self):
        try:
            query = f"""CREATE TABLE IF NOT EXISTS {self.__table} (
                {self.__primary_key} TEXT PRIMARY KEY,
                sha_256 TEXT,
                filename TEXT,
                created_at TEXT
            );"""
            self.execute(query)
        except Exception:
            raise

    def create(self, key, sha_256, filename):
        query = f'INSERT INTO {self.__table} ({self.__primary_key}, sha_256, filename, created_at) VALUES (?, ?, ?, ?);'
        self.execute(query, (key, sha_256, filename, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.__connection.commit()

    def find(self, value):
        return self.where(self.__primary_key, value)

    def where(self, column, value, operator='='):
        query = f'SELECT * FROM {self.__table} WHERE {column} {operator} ?;'
        self.execute(query, (value,))
        return self.__cursor.fetchall()

    def exists(self, value):
        return len(self.find(value)) > 0

    def existsSHA(self, value):
        return len(self.where('sha_256', value)) > 0
