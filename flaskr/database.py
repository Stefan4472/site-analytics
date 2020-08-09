import sqlite3


class Database:
    def __init__(
            self, 
            db_path: str,
    ):
        self.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.row_factory = sqlite3.Row
        self.cur = self.db.cursor()

    def execute_script(self, script_str):
        self.cur.executescript(script_str)

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()

    def record_view(
            self,
            viewed_url: str,
            ip_address: str,
            user_agent: str,
    ):
        query = 'insert into Views values (NULL, ?, ?, ?)'
        values = (viewed_url, ip_address, user_agent)
        self.cur.execute(query, values)
