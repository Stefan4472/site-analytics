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

    def execute_script(
            self, 
            script_str: str,
    ):
        self.cur.executescript(script_str)

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()

    def create_user(
            self,
            ip_address: str,
            commit: bool = False,
    ) -> user.User:
        # Insert
        command = 'insert into _Users(_ip_address) values (?)'
        values = (ip_address,)
        self.cur.execute(command, values)
        if commit:
            self.commit()
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
                user_data['_hostname'],
                user_data['_domain'],
                user_data['_city'],
                user_data['_region'],
                user_data['_country'],
            )

    def get_user_by_id(
            self,
            id: int,
    ) -> typing.Optional[user.User]:
        command = 'select * from _Users where _user_id = ?'
        values = (id,)
        user_data = self.cur.execute(command, values).fetchone()
        if user_data is None:
            return None
        else:
            return user.User(
                user_data['_user_id'],
                user_data['_ip_address'],
                user_data['_hostname'],
                user_data['_domain'],
                user_data['_city'],
                user_data['_region'],
                user_data['_country'],
            )

    def update_user(
            self,
            user: user.User,
            commit: bool = False,
    ):
        command = \
            'update _Users set ' \
                '_hostname = ?,' \
                '_domain = ?,' \
                '_city = ?,' \
                '_region = ? ' \
                '_country = ? ' \
                'where _user_id = ?'
        values = (
            user.hostname,
            user.domain,
            user.city,
            user.region,
            user.country,
            user.user_id,
        )
        self.cur.execute(command, values)
        if commit:
            self.commit()

    def create_session(
            self,
            user: user.User,
            start_time: datetime.datetime,
            commit: bool = False,
    ) -> typing.Optional[session.Session]:
        # Insert
        command = \
            'insert into _Sessions(' \
            '_user_id, _first_request_time, _last_request_time, _num_requests)' \
            ' values (?, ?, ?, ?)'
        values = (
            user.user_id,
            start_time,
            start_time,
            0,
        )
        self.cur.execute(command, values)
        if commit:
            self.commit()
        # Retrieve and return
        return self.get_session(user, start_time)

    def get_session(
            self,
            user: user.User,
            start_time: datetime.datetime,
    ) -> typing.Optional[session.Session]:
        command = 'select * from _Sessions where _user_id = ? AND' \
            ' _first_request_time = ?'
        values = (user.user_id, start_time)
        session_data = self.cur.execute(command, values).fetchone()
        return session.Session(
            session_data['_session_id'],
            session_data['_user_id'],
            datetime.datetime.strptime(session_data['_first_request_time'], '%Y-%m-%d %H:%M:%S.%f'),
            datetime.datetime.strptime(session_data['_last_request_time'], '%Y-%m-%d %H:%M:%S.%f'),
            session_data['_num_requests'],
        )

    def get_session_by_id(
            self,
            session_id: int,
    ) -> typing.Optional[session.Session]:
        command = 'select * from _Sessions where _session_id = ?'
        values = (session_id,)
        session_data = self.cur.execute(command, values).fetchone()
        if session_data:
            return session.Session(
                session_data['_session_id'],
                session_data['_user_id'],
                datetime.datetime.strptime(session_data['_first_request_time'], '%Y-%m-%d %H:%M:%S.%f'),
                datetime.datetime.strptime(session_data['_last_request_time'], '%Y-%m-%d %H:%M:%S.%f'),
                session_data['_num_requests'],
            )
        else:
            return None

    def update_session(
        self,
        session: session.Session,
        commit: bool = False,
    ):
        command = \
            'update _Sessions ' \
                'set _user_id = ?,' \
                '_first_request_time = ?,' \
                '_last_request_time = ?,' \
                '_num_requests = ? ' \
                'where _session_id = ?'
        values = (
            session.user_id,
            session.first_request_time,
            session.last_request_time,
            session.num_requests,
            session.session_id,
        )
        self.cur.execute(command, values)
        if commit:
            self.commit()

    def record_view(
            self,
            session: session.Session,
            timestamp: datetime.datetime,
            viewed_url: str,
            user_agent: str,
            commit: bool = False,
    ):
        query = 'insert into _Views values (NULL, ?, ?, ?, ?)'
        values = (session.session_id, timestamp, viewed_url, user_agent)
        self.cur.execute(query, values)
        if commit:
            self.commit()

    def lookup_cached_session(
            self,
            user_id: int,
    ) -> typing.Optional[session.Session]:
        """Lookup the `user_id` in the `_CachedSessions` table."""
        command = 'select * from _CachedSessions where _user_id = ?' \
            ' and _certified_stale = ?'
        values = (user_id, 0)
        session_info = self.cur.execute(command, values).fetchone()
        if session_info:
            return self.get_session_by_id(session_info['_session_id'])
        else:
            return None

    def add_session_to_cache(
            self,
            session: session.Session,
            commit: bool = False,
    ):
        command = \
            'insert into _CachedSessions(_session_id, _user_id) values (?, ?)'
        values = (session.session_id, session.user_id)
        self.cur.execute(command, values)
        if commit:
            self.commit()

    def update_cached_session(
            self,
            session: session.Session,
            is_stale: bool,
            commit: bool = False,
    ):
        command = \
            'update _CachedSessions set _certified_stale = ? where _session_id = ?'
        values = (int(is_stale), session.session_id)
        self.cur.execute(command, values)
        if commit:
            self.commit()