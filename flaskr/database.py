import sqlite3
import datetime
import typing
from . import user
from . import session


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

    def create_user(
            self,
            ip_address: str,
    ) -> user.User:
        # Insert
        command = 'insert into _Users values (NULL, ?, ?)'
        values = (ip_address, '')
        self.cur.execute(command, values)
        # Retrieve and return
        return self.get_user(ip_address)
        
    def get_user(
            self,
            ip_address: str,
    ) -> typing.Optional[user.User]:
        """Looks up the given IP address and checks if a user is registered
        under it. If not, will register a new user. Returns a User instance.
        """
        # TODO: THROW EXCEPTION IF USER IS NOT FOUND?
        command = 'select * from _Users where _ip_address = ?'
        values = (ip_address,)
        user_data = self.cur.execute(command, values).fetchone()
        if user_data is None:
            return None
        else:
            return user.User(
                user_data['_user_id'], 
                user_data['_ip_address'],
                user_data['_location'],
            )

    def create_session(
            self,
            user: user.User,
            start_time: datetime.datetime,
    ) -> typing.Optional[session.Session]:
        # Insert
        command = 'insert into _Sessions values (NULL, ?, ?, ?, ?, ?, ?)'
        values = (
            user.user_id,
            start_time.date(),
            start_time.date(),
            0,
        )
        self.cur.execute(command, values)
        # Retrieve and return
        return self.get_session(user, start_time)

    def get_session(
            self,
            user: user.User,
            start_time: datetime.datetime,
    ) -> typing.Optional[session.Session]:
        command = 'select * from _Sessions where _user_id = ? AND' \
            ' _first_request_time = ?'
        values = (user.user_id, start_time.date())
        session_data = self.cur.execute(command, values).fetchone()
        return session.Session(
            session_data['_session_id'],
            session_data['_user_id'],
            session_data['_first_request_time'],
            session_data['_last_request_time'],
            session_data['_num_requests'],
        )

    # def record_view(
    #         self,
    #         viewed_url: str,
    #         ip_address: str,
    #         user_agent: str,
    # ):
    #     query = 'insert into Views values (NULL, ?, ?, ?)'
    #     values = (viewed_url, ip_address, user_agent)
    #     self.cur.execute(query, values)
