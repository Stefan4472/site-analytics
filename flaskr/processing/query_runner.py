import sqlalchemy.engine
import sqlalchemy as sqla
import datetime as dt
import dataclasses as dc
from enum import Enum
from typing import Optional, List
import flaskr.processing.util as util


class QueryOn(Enum):
    People = 'People'
    Bots = 'Bots'


class CountWhat(Enum):
    Views = 'Views'
    Users = 'Users'


class GroupWhat(Enum):
    Nothing = 'Nothing'
    Country = 'Country'
    City = 'City'
    Region = 'Region'
    Url = 'Url'
    Domain = 'Domain'
    OperatingSystem = 'OperatingSystem'
    # TODO: remaining user-agent infos

    def get_column_name(self) -> Optional[str]:
        if self == GroupWhat.Nothing:
            return None
        elif self == GroupWhat.Country:
            return '_user.country'
        elif self == GroupWhat.City:
            return '_user.city'
        elif self == GroupWhat.Region:
            return '_user.region'
        elif self == GroupWhat.Url:
            return 'view.url'
        elif self == GroupWhat.Domain:
            return '_user.domain'
        elif self == GroupWhat.OperatingSystem:
            return 'view.operating_system'
        else:
            raise ValueError('Not implemented')


class QueryResolution(Enum):
    AllTime = 'AllTime'
    Day = 'Day'
    Week = 'Week'
    Month = 'Month'
    Year = 'Year'


@dc.dataclass
class Query:
    query_on: QueryOn
    count_what: CountWhat
    group_what: GroupWhat
    resolution: QueryResolution
    start_date: dt.date = None
    end_date: dt.date = None


@dc.dataclass
class QueryResult:
    quantity: int
    date: dt.datetime = None
    key: str = None


class QueryRunner:
    """
    Dynamically generate and execute queries.

    This is pretty complicated, but it's the only feasible way to cover
    all TimePeriod * Selection combinations. I don't know if this will
    be the way-to-go long term, because it makes schema changes tough.

    See `test_query_runner.py` for examples of queries and generated SQL.
    """
    @staticmethod
    def run_query(
            query: Query,
            session: 'sqlalchemy.orm.scoping.scoped_session',
    ) -> List[QueryResult]:
        sql = sqla.text(QueryRunner._generate_sql(query))
        params = {
            'is_bot': query.query_on == QueryOn.Bots,
            'start': query.start_date if query.start_date else dt.date.min,
            'end': query.end_date if query.end_date else dt.date.max,
        }
        result = session.execute(sql, params)
        return QueryRunner._make_results(query, result)

    @staticmethod
    def _generate_sql(query: Query) -> str:
        """
        Dynamically generate SQL for the given query.

        This is a little hairy. I've done my best to make it readable.
        There are still some logic simplifications that could be done in the
        GROUP BY section.
        """
        if query.count_what == CountWhat.Users:
            query_string = 'SELECT COUNT(DISTINCT _user.id) AS cnt'
        else:
            query_string = 'SELECT COUNT(*) AS cnt'

        # Select specified "QueryWhat" column
        if query.group_what != GroupWhat.Nothing:
            query_string += ', ' + query.group_what.get_column_name()

        # Select date values for "QueryResolution" (if resolution != AllTime)
        if query.resolution == QueryResolution.Day:
            query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year, EXTRACT(DOY FROM view.timestamp) AS day'
        elif query.resolution == QueryResolution.Week:
            query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year, EXTRACT(WEEK FROM view.timestamp) AS week'
        elif query.resolution == QueryResolution.Month:
            query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year, EXTRACT(MONTH FROM view.timestamp) AS month'
        elif query.resolution == QueryResolution.Year:
            query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year'

        query_string += \
            ' FROM _user JOIN view ON view.user_id = _user.id ' \
            'WHERE view.timestamp > :start AND view.timestamp < :end ' \
            'AND _user.is_bot = :is_bot'

        # Assemble GROUP BY (unless resolution == AllTime and QueryWhat == Nothing)
        if not (query.resolution == QueryResolution.AllTime and query.group_what == GroupWhat.Nothing):
            query_string += ' GROUP BY '
            if query.resolution == QueryResolution.AllTime:
                # No dates involved: just GROUP BY the selected column
                query_string += query.group_what.get_column_name()
            else:
                # GROUP BY date first
                if query.resolution == QueryResolution.Day:
                    query_string += 'year, day'
                elif query.resolution == QueryResolution.Week:
                    query_string += 'year, week'
                elif query.resolution == QueryResolution.Month:
                    query_string += 'year, month'
                elif query.resolution == QueryResolution.Year:
                    query_string += 'year'
                # Then GROUP BY selected column
                if query.group_what != GroupWhat.Nothing:
                    query_string += ', ' + query.group_what.get_column_name()

        query_string += ' ORDER BY '
        # ORDER BY date if resolution != AllTime
        if query.resolution == QueryResolution.Day:
            query_string += 'year, day, '
        elif query.resolution == QueryResolution.Week:
            query_string += 'year, week, '
        elif query.resolution == QueryResolution.Month:
            query_string += 'year, month, '
        elif query.resolution == QueryResolution.Year:
            query_string += 'year, '
        # Then order by "QueryWhat" column
        if query.group_what == GroupWhat.Nothing:
            query_string += 'cnt'
        else:
            query_string += query.group_what.get_column_name()

        return query_string

    @staticmethod
    def _make_results(
            query: Query,
            result: sqlalchemy.engine.CursorResult,
    ) -> List[QueryResult]:
        """
        Given an SQLAlchemy Cursor that resulted from executing the query,
        return a list of QueryResults.
        """
        has_key = (query.group_what != GroupWhat.Nothing)
        # The index at which date information starts depends on whether
        # we queried on something besides the total count.
        date_index = 2 if has_key else 1

        if query.resolution == QueryResolution.AllTime:
            return [QueryResult(r[0], key=r[1] if has_key else None) for r in result.all()]
        elif query.resolution == QueryResolution.Day:
            return [QueryResult(r[0], key=r[1] if has_key else None, date=util.datetime_from_day(r[date_index], r[date_index+1])) for r in result.all()]
        elif query.resolution == QueryResolution.Week:
            return [QueryResult(r[0], key=r[1] if has_key else None, date=util.datetime_from_week(r[date_index], r[date_index+1])) for r in result.all()]
        elif query.resolution == QueryResolution.Month:
            return [QueryResult(r[0], key=r[1] if has_key else None, date=util.datetime_from_month(r[date_index], r[date_index+1])) for r in result.all()]
        elif query.resolution == QueryResolution.Year:
            return [QueryResult(r[0], key=r[1] if has_key else None, date=util.datetime_from_year(r[date_index])) for r in result.all()]
