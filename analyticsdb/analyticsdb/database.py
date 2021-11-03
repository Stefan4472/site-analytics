import sqlite3
import datetime
import enum
import typing
from . import user
from . import session
from . import dto
from . import dbutil


class Classification(enum.Enum):
    USER = 'USER'
    BOT = 'BOT'


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
                user_data['_classification'],
                user_data['_was_processed'],
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
                user_data['_classification'],
                user_data['_was_processed'],
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
                '_region = ?, ' \
                '_country = ?, ' \
                '_classification = ?, ' \
                '_was_processed = ? ' \
                'where _user_id = ?'
        values = (
            user.hostname,
            user.domain,
            user.city,
            user.region,
            user.country,
            user.classification,
            int(user.was_processed),
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
            self._parse_datetime(session_data['_first_request_time']),
            self._parse_datetime(session_data['_last_request_time']),
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
                self._parse_datetime(session_data['_first_request_time']),
                self._parse_datetime(session_data['_last_request_time']),
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
        query = \
            'insert into _Views' \
                '(_session_id, _user_id, _timestamp, _url, _user_agent) ' \
                'values (?, ?, ?, ?, ?)'
        values = (
            session.session_id, 
            session.user_id, 
            timestamp, 
            viewed_url, 
            user_agent,
        )
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

    def gen_all_cached_sessions(
            self,
    ) -> typing.Generator[session.Session, None, None]:
        """TODO: NOTE: THE CURRENT WAY WE DO THIS IS PRETTY INEFFICIENT."""
        command = 'select * from _CachedSessions'
        for cached_session in self.cur.execute(command).fetchall():
            yield self.get_session_by_id(cached_session['_session_id'])

    def cleanup_cached_sessions(
            self,
            commit: bool = False,
    ) -> int:
        """Go through the `_CachedSessions` table, checking for stale records
        and removing stale records."""
        # Get all records that are not marked stale
        command = 'select * from _CachedSessions where _certified_stale = ?'
        values = (0,)
        for active_record in self.cur.execute(command, values).fetchall():
            print('Found cached session {}'.format(active_record['_session_id']))
            session = self.get_session_by_id(active_record['_session_id'])
            if not session.is_active():
                print('Session is inactive (id={})'.format(session.session_id))
                self.update_cached_session(session, is_stale=True)
        # Count number of stale records
        count_command = \
            'select Count(*) from _CachedSessions where _certified_stale = ?'
        count_values = (1,)
        self.cur.execute(count_command, count_values)
        rows_deleted = self.cur.fetchone()[0]
        # Drop all records that are stale
        drop_command = 'delete from _CachedSessions where _certified_stale = ?'
        drop_values = (1,)
        self.cur.execute(drop_command, drop_values)
        if commit:
            self.commit()
        return rows_deleted

    '''Start analytics functions '''
    def get_unique_ips(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
    ) -> [dto.UserBotDateResult]:
        """Get unique users timeboxed by week of year."""
        query = \
            'SELECT strftime("%Y-%W", s._first_request_time) AS Week, _classification, COUNT(*) ' \
            'FROM _Users AS u ' \
            'JOIN _Sessions AS s ON u._user_id = s._user_id ' \
            'WHERE s._first_request_time > ? AND s._first_request_time < ? ' \
            'GROUP BY _classification, strftime("%Y%W", s._first_request_time)' \
            'ORDER BY s._first_request_time ASC'
        values = (start_date, end_date)
        result = self.cur.execute(query, values)
        return dbutil.format_timeboxed_result(result)

    def get_views(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
    ) -> [dto.UserBotDateResult]:
        """Get site hits timeboxed by week of year."""
        query = \
            'SELECT strftime("%Y-%W", v._timestamp) AS Week, _classification, COUNT(*) ' \
            'FROM _Users AS u ' \
            'JOIN _Views AS v ON u._user_id = v._user_id ' \
            'WHERE v._timestamp > ? AND v._timestamp < ? ' \
            'GROUP BY _classification, strftime("%Y%W", v._timestamp) ' \
            'ORDER BY v._timestamp ASC'
        values = (start_date, end_date)
        result = self.cur.execute(query, values)
        return dbutil.format_timeboxed_result(result)

    def get_countries(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            classification: Classification,
    ) -> [dto.CountryResult]:
        """Get number of views per country for the given classification."""
        query = \
            'SELECT _country, COUNT(*) ' \
            'FROM _Views AS v ' \
            'JOIN _Users AS u ON v._user_id = u._user_id ' \
            'WHERE u._classification = ? AND v._timestamp > ? AND v._timestamp < ? ' \
            'GROUP BY _country ' \
            'ORDER BY COUNT(*) DESC'
        values = (classification.value, start_date, end_date)
        res = self.cur.execute(query, values)
        return [dto.CountryResult(row[0], row[1]) for row in res.fetchall()]


    def get_cities(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            classification: Classification,
    ) -> [dto.CountryResult]:
        """Get number of views per city for the given classification."""
        query = \
            'SELECT _city, COUNT(*) ' \
            'FROM _Views AS v ' \
            'JOIN _Users AS u ON v._user_id = u._user_id ' \
            'WHERE u._classification = ? AND v._timestamp > ? AND v._timestamp < ? ' \
            'GROUP BY _country ' \
            'ORDER BY COUNT(*) DESC'
        values = (classification.value, start_date, end_date)
        res = self.cur.execute(query, values)
        return [dto.CityResult(row[0], row[1]) for row in res.fetchall()]

    def get_urls(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            classification: Classification,
    ) -> [dto.PostResult]:
        """Get number of views per url for the given classification."""
        query = \
            'SELECT v._url, COUNT(*) ' \
            'FROM _Views AS v ' \
            'JOIN _Users as u on v._user_id = u._user_id ' \
            'WHERE u._classification = ? AND v._timestamp > ? AND v._timestamp < ? ' \
            'GROUP BY _url ' \
            'ORDER BY COUNT(*) DESC'
        values = (classification.value, start_date, end_date)
        res = self.cur.execute(query, values)
        return [dto.PostResult(row[0], row[1]) for row in res.fetchall()]

    def get_hostnames(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            classification: Classification,
    ) -> [dto.HostnameResult]:
        """Get number of views by hostname for the given classification."""
        query = 'SELECT _domain, COUNT(*) ' \
                'FROM _Views AS v ' \
                'JOIN _Users AS u ON v._user_id = u._user_id ' \
                'WHERE u._classification = ? AND v._timestamp > ? AND v._timestamp < ? ' \
                'GROUP BY _country ' \
                'ORDER BY COUNT(*) DESC'
        values = (classification.value, start_date, end_date)
        res = self.cur.execute(query, values)
        return [dto.HostnameResult(row[0], row[1]) for row in res.fetchall()]

    def _parse_datetime(self, date_str: str) -> datetime.datetime:
        try:
            # Sometimes this doesn't work. Some kind of SQL oddity
            return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError as e:
            pass
        return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
