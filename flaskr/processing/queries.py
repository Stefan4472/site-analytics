import typing
import datetime as dt
import sqlalchemy as sqla
from flaskr import db
from flaskr.processing.query_runner import QueryRunner, QueryWhat, QueryOn, QueryWhat, QueryResolution
import flaskr.processing.dto as dto
from flaskr.contracts.data_request import UserBotClassification
"""
Dynamic generation of queries turned out to be too much hassle.
Rather a bit of mostly-repeated code that is easy to understand
and debug than an uber-complex function.
"""


def query_users(
        what: QueryWhat,
        classification: UserBotClassification,
        start_date: dt.date,
        end_date: dt.date,
        resolution: QueryResolution,
) -> [dto.QuantityResult]:
    builder = QueryRunner(QueryOn.Users, what, resolution)
    # query = sqla.text(
    #     'SELECT COUNT(*), EXTRACT(YEAR FROM v.timestamp) AS year, EXTRACT(MONTH FROM v.timestamp) AS month '
    #     'FROM _user AS u '
    #     'JOIN view AS v ON v.user_id = u.id '
    #     'WHERE v.timestamp > :start AND v.timestamp < :end '
    #     'AND u.is_bot = :is_bot '
    #     'GROUP BY year, month '
    #     'ORDER BY year, month'
    # )
    # print(_make_results(list(results), resolution))
    # return [dto.QuantityResult(r[0], dt.datetime(int(r[1]), int(r[2]), 1)) for r in results]
    return builder.run_query(db.session, start_date, end_date, classification)


def query_views(
        what: QueryWhat,
        classification: UserBotClassification,
        start_date: dt.date,
        end_date: dt.date,
        resolution: QueryResolution,
) -> [dto.QuantityResult]:
    """Get number of views timeboxed by month of year."""
    # query = sqla.text(
    #     'SELECT COUNT(*), EXTRACT(YEAR FROM v.timestamp) AS year, EXTRACT(MONTH FROM v.timestamp) AS month '
    #     'FROM _user AS u '
    #     'JOIN view AS v ON v.user_id = u.id '
    #     'WHERE v.timestamp > :start AND v.timestamp < :end '
    #     'AND u.is_bot = :is_bot '
    #     'GROUP BY year, month '
    #     'ORDER BY year, month'
    # )
    # params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    # results = db.session.execute(query, params)
    # print(type(results))
    # return [dto.QuantityResult(r[0], dt.datetime(int(r[1]), int(r[2]), 1)) for r in results]
    builder = QueryRunner(QueryOn.Views, what, resolution)
    return builder.run_query(db.session, start_date, end_date, classification)


# TODO: probably just provide one "location" query that groups by city and country
def get_countries(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.CountryResult]:
    """Number of unique users by country, timeboxed by month of year"""
    query = sqla.text(
        'SELECT u.country, COUNT(DISTINCT u.id) AS num '
        'FROM _user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY u.country '
        'ORDER BY num DESC'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.CountryResult(r[0], r[1]) for r in results]


def get_cities(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.CityResult]:
    query = sqla.text(
        'SELECT u.city, COUNT(DISTINCT u.id) as num '
        'FROM _user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY u.city '
        'ORDER BY num DESC'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.CityResult(*r) for r in results]


def get_urls(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.UrlResult]:
    """Return number of views per URL, timeboxed by month of year."""
    query = sqla.text(
        'SELECT v.url, COUNT(*) AS num '
        'FROM _user AS u '
        'JOIN view AS v on v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY v.url '
        'ORDER BY num DESC'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.UrlResult(*r) for r in results]


def get_hostnames(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.HostnameResult]:
    query = sqla.text(
        'SELECT u.domain, COUNT(*) AS num '
        'FROM _user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY u.domain '
        'ORDER BY num DESC'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.HostnameResult(*r) for r in results]


def _make_query(
        query_type: QueryOn,
        resolution: QueryResolution,
) -> str:
    """Dynamically build the query. This is a little hairy."""
    if query_type == QueryOn.Users:
        query_string = 'SELECT COUNT(DISTINCT _user.id) AS cnt'
    else:
        query_string = 'SELECT COUNT(*) AS cnt'

    if resolution == QueryResolution.Day:
        query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year, EXTRACT (DOY FROM view.timestamp) AS day'
    elif resolution == QueryResolution.Week:
        query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year, EXTRACT (WEEK FROM view.timestamp) AS week'
    elif resolution == QueryResolution.Month:
        query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year, EXTRACT (MONTH FROM view.timestamp) AS month'
    elif resolution == QueryResolution.Year:
        query_string += ', EXTRACT(YEAR FROM view.timestamp) AS year'

    query_string += \
        ' FROM _user JOIN view ON view.user_id = _user.id ' \
        'WHERE view.timestamp > :start AND view.timestamp < :end ' \
        'AND _user.is_bot = :is_bot'

    if resolution == QueryResolution.Day:
        query_string += ' GROUP BY year, day ORDER BY year, day'
    elif resolution == QueryResolution.Week:
        query_string += ' GROUP BY year, week ORDER BY year, week'
    elif resolution == QueryResolution.Month:
        query_string += ' GROUP BY year, month ORDER BY year, month'
    elif resolution == QueryResolution.Year:
        query_string += ' GROUP BY year ORDER BY year'

    return query_string


def _make_results(
        tuples: typing.List[typing.Tuple],
        resolution: QueryResolution,
):
    if resolution == QueryResolution.AllTime:
        return [dto.QueryResult(t[0]) for t in tuples]
    elif resolution == QueryResolution.Day:
        return [dto.QueryResult(t[0], date=_dt_from_day(t[1], t[2])) for t in tuples]
    elif resolution == QueryResolution.Week:
        return [dto.QueryResult(t[0], date=_dt_from_week(t[1], t[2])) for t in tuples]
    elif resolution == QueryResolution.Month:
        return [dto.QueryResult(t[0], date=_dt_from_month(t[1], t[2])) for t in tuples]
    elif resolution == QueryResolution.Year:
        return [dto.QueryResult(t[0], date=_dt_from_year(t[1])) for t in tuples]


def _dt_from_day(year: float, day_of_year: float) -> dt.datetime:
    """Construct a datetime instance given the day-of-the-year and the year."""
    as_string = f'{int(year)}-{int(day_of_year)}'
    # %Y: 4-digit year
    # %j: Day of the year
    return dt.datetime.strptime(as_string, '%Y-%j')


def _dt_from_week(year: float, week_of_year: float) -> dt.datetime:
    """
    Construct a datetime instance given the year and the week of the year.
    Sets the date to the Monday of that week.
    The only way I've found to do this is with strptime.
    """
    as_string = f'{int(year)}-{int(week_of_year)}-1'
    # %Y: 4-digit year
    # %W: Week number of the year
    # %w: Weekday starting with 0=Sunday (set to 1 for Monday, above)
    return dt.datetime.strptime(as_string, '%Y-%W-%w')


def _dt_from_month(year: float, month_of_year: float) -> dt.datetime:
    """
    Construct a datetime instance given the year and the month of the year.
    Sets the date to the 1st of that month.
    """
    as_string = f'{int(year)}-{int(month_of_year)}-1'
    # %Y: 4-digit year
    # %m: month of the year
    # %d: day of the month
    return dt.datetime.strptime(as_string, '%Y-%m-%d')


def _dt_from_year(year: float) -> dt.datetime:
    """
    Construct a datetime instance given the year.
    Set the date to January 1st of that year.
    """
    as_string = f'{int(year)}-1-1'
    # %Y: 4-digit year
    # %m: month of the year
    # %d: day of the month
    return dt.datetime.strptime(as_string, '%Y-%m-%d')
