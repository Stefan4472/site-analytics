import datetime as dt
import sqlalchemy as sqla
from flaskr import db
from flaskr.models.user import User
from flaskr.models.view import View
# NOTE: Performance isn't a concern right now


def get_users(start_date: dt.datetime, end_date: dt.datetime, is_bot: bool):
    """Get unique users timeboxed by week of year."""
    # TODO: THIS QUERY ISN'T CORRECT
    print(db.session.query(User.id))
    query = sqla.text(
        'SELECT strftime("%Y-%W", v.timestamp) AS Week, COUNT(*) '
        'FROM user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY strftime("%Y%W", v.timestamp) '
        'ORDER BY v.timestamp ASC'
    )
    params = {'is_bot': is_bot, 'start': start_date, 'end': end_date}
    result = db.session.execute(query, params)
    print(result.all())


def get_views(start_date: dt.datetime, end_date: dt.datetime, is_bot: bool):
    query = sqla.text(
        'SELECT strftime("%Y-%W", v.timestamp) AS Week, COUNT(*) '
        'FROM user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY strftime("%Y%W", v.timestamp) '
        'ORDER BY v.timestamp ASC'
    )
    params = {'is_bot': is_bot, 'start': start_date, 'end': end_date}
    result = db.session.execute(query, params)
    print(result.all())

    # res = db.session.query(sqla.func.count(View.id))\
    #     .where(View.user.was_processed)\
    #     .where(View.user.is_bot)\
    #     .group_by(sqla.func.strftime("%Y-%m-%d", View.timestamp))\
    #     .all()
    # print(res)


def get_countries(start_date: dt.datetime, end_date: dt.datetime, is_bot: bool):
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
    params = {'is_bot': is_bot, 'start': start_date, 'end': end_date}
    result = db.session.execute(query, params)
    print(result.all())


def get_cities(start_date: dt.datetime, end_date: dt.datetime, is_bot: bool):
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
    params = {'is_bot': is_bot, 'start': start_date, 'end': end_date}
    result = db.session.execute(query, params)
    print(result.all())


def get_urls(start_date: dt.datetime, end_date: dt.datetime, is_bot: bool):
    query = sqla.text(
        'SELECT v.url, COUNT(*) '
        'FROM user AS u '
        'JOIN view AS v on v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY v.url '
        'ORDER BY COUNT(*) DESC'
    )
    params = {'is_bot': is_bot, 'start': start_date, 'end': end_date}
    result = db.session.execute(query, params)
    print(result.all())


def get_hostnames(start_date: dt.datetime, end_date: dt.datetime, is_bot: bool):
    query = sqla.text(
        'SELECT u.domain, COUNT(*) '
        'FROM user AS u '
        'JOIN view AS v ON v.user_id = u.id '
        'WHERE v.timestamp > :start AND v.timestamp < :end '
        'AND u.is_bot = :is_bot '
        'GROUP BY u.country '
        'ORDER BY COUNT(*) DESC'
    )
    params = {'is_bot': is_bot, 'start': start_date, 'end': end_date}
    result = db.session.execute(query, params)
    print(result.all())
