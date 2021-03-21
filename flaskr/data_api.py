import typing
import datetime
import pathlib
import json
from flask import Blueprint, g, current_app, request, Response, jsonify
from analyticsdb import database
from analyticsdb import user as us
from analyticsdb import session as se
from . import database_context as db_context


# Create blueprint, which will be used to register URL routes
blueprint = Blueprint('data', __name__, url_prefix='/api/v1/data')


def parse_date(date_str: str) -> datetime:
    """Parses a string date in format YYYY-MM-DD."""
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')


# TODO: WILL NEED WORK. CREATE AN 'ARGS' OBJECT?
# parse_args returns Args object. Takes 'start_date_reqd' boolean parameters, which will throw ValueError if not present.
# Can have custom exception type that provides message and error status code
def parse_args(args, start_date=True, end_date=True):
    if start_date and 'start_date' not in args:
        raise ValueError('Missing start_date')
    if end_date and 'end_date' not in args:
        raise ValueError('Missing end_date')

    start_date = parse_date(request.args['start_date'])
    end_date = parse_date(request.args['end_date'])
    return start_date, end_date


# TODO: VARIABLE INTERVALS
@blueprint.route('/unique-users')
def get_unique_users():
    try:
        start_date, end_date = parse_args(request.args)
        db = db_context.get_db()
        res = db.get_unique_users(start_date, end_date)
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/views')
def get_views():
    if 'start_date' not in request.args:
        return Response('Missing start_date', status=400)
    if 'end_date' not in request.args:
        return Response('Missing end_date', status=400)

    start_date = parse_date(request.args['start_date'])
    end_date = parse_date(request.args['end_date'])

    query = 'SELECT strftime("%Y-%W", v._timestamp) AS Week, _classification, COUNT(*) ' \
            'FROM _Users AS u ' \
            'JOIN _Views AS v ON u._user_id = v._user_id ' \
            'WHERE v._timestamp > ? AND v._timestamp < ? ' \
            'GROUP BY _classification, strftime("%Y%W", v._timestamp)'
    values = (start_date, end_date)
    res = db_context.get_db().cur.execute(query, values)

    # TODO: SORT FIRST, THEN BUILD OBJECTS
    res_by_date = {}
    for row in res.fetchall():
        if row[0] in res_by_date:
            res_by_date[row[0]][row[1]] = row[2]
        else:
            res_by_date[row[0]] = {row[1]: row[2]}

    return jsonify([{'date': k, 'user': v['USER'], 'bot': v['BOT']} for k, v in res_by_date.items()])
