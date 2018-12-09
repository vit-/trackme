import sqlite3
from contextlib import contextmanager


class DBMixin(object):

    db_file = None

    @property
    @contextmanager
    def db(self):
        conn = sqlite3.connect(self.db_file)
        try:
            yield conn
        finally:
            conn.close()
