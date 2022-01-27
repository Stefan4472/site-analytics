import sqlalchemy.engine
import sqlalchemy as sqla
import datetime as dt
from enum import Enum
from flaskr.contracts.data_request import UserBotClassification
import flaskr.processing.util as util
from flaskr.processing.dto import QueryResult


# TODO: I'm not perfectly happy with the names yet.
class QueryOn(Enum):
    Users = 'Users'
    Views = 'Views'


class QueryWhat(Enum):
    Nothing = 'Nothing'
    Country = 'Country'
    City = 'City'
    Region = 'Region'
    Url = 'Url'
    Domain = 'Domain'
    OperatingSystem = 'OperatingSystem'
    # TODO: remaining user-agent infos


class QueryResolution(Enum):
    AllTime = 'AllTime'
    Day = 'Day'
    Week = 'Week'
    Month = 'Month'
    Year = 'Year'


class QueryRunner:
    """
    Dynamically generate and execute queries.

    This is pretty complicated, but it's the only feasible way to cover
    all TimePeriod * Selection combinations. I don't know if this will
    be the way-to-go long term, because it makes schema changes tough.

    See `test_query_runner.py` for examples of generated queries.
    """
    def __init__(
            self,
            query_on: QueryOn,
            query_what: QueryWhat,
            resolution: QueryResolution,
    ):
        self.query_on = query_on
        self.query_what = query_what
        self.resolution = resolution

    def run_query(
            self,
            session: 'sqlalchemy.orm.scoping.scopred_session',
            start_date: dt.date,
            end_date: dt.date,
            classification: UserBotClassification,
    ):
        query = sqla.text(self._make_query())
        params = {
            'is_bot': classification.is_bot(),
            'start': start_date,
            'end': end_date,
        }
        result = session.execute(query, params)
        return self._make_results(result)

    def _make_query(self) -> str:
        """Dynamically build the query. This is a little hairy."""
        if self.query_on == QueryOn.Users:
            query_string = 'SELECT COUNT(DISTINCT _user.id) AS cnt'
        else:
            query_string = 'SELECT COUNT(*) AS cnt'

        # TODO: could bypass this by providing a QueryWhat.get_col_name()
        if self.query_what == QueryWhat.Nothing:
            pass
        elif self.query_what == QueryWhat.Country:
            query_string += ', _user.country'
        elif self.query_what == QueryWhat.City:
            query_string += ', _user.city'
        elif self.query_what == QueryWhat.Region:
            query_string += ', _user.region'
        elif self.query_what == QueryWhat.Url:
            query_string += ', view.url'
        elif self.query_what == QueryWhat.Domain:
            query_string += ', _user.domain'
        elif self.query_what == QueryWhat.OperatingSystem:
            query_string += ', view.operating_system'
        else:
            raise ValueError('Unsupported "Query.What"')

        if self.resolution == QueryResolution.Day:
            query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year, EXTRACT(DOY FROM view.timestamp) AS day'
        elif self.resolution == QueryResolution.Week:
            query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year, EXTRACT(WEEK FROM view.timestamp) AS week'
        elif self.resolution == QueryResolution.Month:
            query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year, EXTRACT(MONTH FROM view.timestamp) AS month'
        elif self.resolution == QueryResolution.Year:
            query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year'

        query_string += \
            ' FROM _user JOIN view ON view.user_id = _user.id ' \
            'WHERE view.timestamp > :start AND view.timestamp < :end ' \
            'AND _user.is_bot = :is_bot'

        if self.resolution == QueryResolution.Day:
            query_string += ' GROUP BY year, day'
        elif self.resolution == QueryResolution.Week:
            query_string += ' GROUP BY year, week'
        elif self.resolution == QueryResolution.Month:
            query_string += ' GROUP BY year, month'
        elif self.resolution == QueryResolution.Year:
            query_string += ' GROUP BY year'

        # Depending on whether we already had a GROUP BY
        if self.resolution == QueryResolution.AllTime:
            if self.query_what == QueryWhat.Country:
                query_string += ' GROUP BY _user.country'
            elif self.query_what == QueryWhat.City:
                query_string += ' GROUP BY _user.city'
            elif self.query_what == QueryWhat.Region:
                query_string += ' GROUP BY _user.region'
            elif self.query_what == QueryWhat.Url:
                query_string += ' GROUP BY view.url'
            elif self.query_what == QueryWhat.Domain:
                query_string += ' GROUP BY _user.domain'
            elif self.query_what == QueryWhat.OperatingSystem:
                query_string += ' GROUP BY view.operating_system'
        else:
            if self.query_what == QueryWhat.Country:
                query_string += ', _user.country'
            elif self.query_what == QueryWhat.City:
                query_string += ', _user.city'
            elif self.query_what == QueryWhat.Region:
                query_string += ', _user.region'
            elif self.query_what == QueryWhat.Url:
                query_string += ', view.url'
            elif self.query_what == QueryWhat.Domain:
                query_string += ', _user.domain'
            elif self.query_what == QueryWhat.OperatingSystem:
                query_string += ', view.operating_system'

        if self.resolution == QueryResolution.Day:
            query_string += ' ORDER BY year, day'
        elif self.resolution == QueryResolution.Week:
            query_string += ' ORDER BY year, week'
        elif self.resolution == QueryResolution.Month:
            query_string += ' ORDER BY year, month'
        elif self.resolution == QueryResolution.Year:
            query_string += ' ORDER BY year'

        if self.query_what == QueryWhat.Nothing:
            query_string += ', cnt'
        if self.query_what == QueryWhat.Country:
            query_string += ', _user.country'
        elif self.query_what == QueryWhat.Region:
            query_string += ', _user.region'
        elif self.query_what == QueryWhat.Url:
            query_string += ', view.url'
        elif self.query_what == QueryWhat.Domain:
            query_string += ', _user.domain'
        elif self.query_what == QueryWhat.OperatingSystem:
            query_string += ', view.operating_system'

        return query_string

    def _make_results(
            self,
            result: sqlalchemy.engine.CursorResult,
    ):
        has_key = False if self.query_what == QueryWhat.Nothing else True
        # The index at which date information starts depends on whether
        # we queried on something besides the total count.
        date_index = 2 if has_key else 1

        if self.resolution == QueryResolution.AllTime:
            return [QueryResult(r[0], key=r[1] if has_key else None) for r in result.all()]
        elif self.resolution == QueryResolution.Day:
            return [QueryResult(r[0], key=r[1] if has_key else None, date=util.datetime_from_day(r[date_index], r[date_index+1])) for r in result.all()]
        elif self.resolution == QueryResolution.Week:
            return [QueryResult(r[0], key=r[1] if has_key else None, date=util.datetime_from_week(r[date_index], r[date_index+1])) for r in result.all()]
        elif self.resolution == QueryResolution.Month:
            return [QueryResult(r[0], key=r[1] if has_key else None, date=util.datetime_from_month(r[date_index], r[date_index+1])) for r in result.all()]
        elif self.resolution == QueryResolution.Year:
            return [QueryResult(r[0], key=r[1] if has_key else None, date=util.datetime_from_year(r[date_index])) for r in result.all()]
