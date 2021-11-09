import datetime as dt
import sqlalchemy as sqla
from flaskr import db
import flaskr.processing.dto as dto
from flaskr.contracts.data_request import UserBotClassification
# TODO: MAKE INTERVALS OPTIONAL AND VARIABLE
# TODO: FIX TIMEBOXING


def get_users(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.QuantityResult]:
    """Get unique users timeboxed by week of year."""
    # TODO: THIS QUERY ISN'T CORRECT
    query = sqla.text(
        'SELECT COUNT(*), strftime("%Y-%W", v.timestamp) AS Week '
        'FROM user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY strftime("%Y%W", v.timestamp) '
        'ORDER BY v.timestamp ASC'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.QuantityResult(*r) for r in results]


def get_views(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.QuantityResult]:
    query = sqla.text(
        'SELECT COUNT(*), strftime("%Y-%W", v.timestamp) AS Week '
        'FROM user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY strftime("%Y%W", v.timestamp) '
        'ORDER BY v.timestamp ASC'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.QuantityResult(*r) for r in results]


def get_countries(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.CountryResult]:
    # TODO: TIMEBOXXING DOESN'T WORK
    query = sqla.text(
        'SELECT country, COUNT(*) '
        'FROM user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY country '
        'ORDER BY COUNT(*) DESC'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.CountryResult(*r) for r in results]


def get_cities(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.CityResult]:
    # TODO: TIMEBOXXING DOESN'T WORK
    query = sqla.text(
        'SELECT city, COUNT(*) '
        'FROM user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY city '
        'ORDER BY COUNT(*) DESC'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.CityResult(*r) for r in results]


def get_urls(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.UrlResult]:
    query = sqla.text(
        'SELECT v.url, COUNT(*) '
        'FROM user AS u '
        'JOIN view AS v on v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY v.url '
        'ORDER BY COUNT(*) DESC'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.UrlResult(*r) for r in results]


def get_hostnames(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.HostnameResult]:
    query = sqla.text(
        'SELECT u.domain, COUNT(*) '
        'FROM user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY u.country '
        'ORDER BY COUNT(*) DESC'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.HostnameResult(*r) for r in results]
