import datetime as dt
import sqlalchemy as sqla
from flaskr import db
import flaskr.processing.dto as dto
from flaskr.contracts.data_request import UserBotClassification
# TODO: MAKE INTERVALS OPTIONAL AND VARIABLE
# TODO: the difference between user queries and view queries is really small. Can generalize the queries, and the result DTOs


def get_users(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.QuantityResult]:
    """Get number of unique users timeboxed by month of year."""
    query = sqla.text(
        'SELECT COUNT(DISTINCT u.id), EXTRACT(YEAR FROM v.timestamp) AS year, EXTRACT(MONTH FROM v.timestamp) AS month '
        'FROM _user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY year, month '
        'ORDER BY year, month'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.QuantityResult(r[0], dt.datetime(int(r[1]), int(r[2]), 1)) for r in results]


def get_views(start_date: dt.date, end_date: dt.date, classification: UserBotClassification) -> [dto.QuantityResult]:
    """Get number of views timeboxed by month of year."""
    query = sqla.text(
        'SELECT COUNT(*), EXTRACT(YEAR FROM v.timestamp) AS year, EXTRACT(MONTH FROM v.timestamp) AS month '
        'FROM _user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY year, month '
        'ORDER BY year, month'
    )
    params = {'is_bot': classification.is_bot(), 'start': start_date, 'end': end_date}
    results = db.session.execute(query, params)
    return [dto.QuantityResult(r[0], dt.datetime(int(r[1]), int(r[2]), 1)) for r in results]


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
