import datetime
from flask import Blueprint, request, Response, jsonify
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


# TODO: MAKE INTERVALS OPTIONAL AND VARIABLE
@blueprint.route('/unique-users-per-week')
def get_unique_users_per_week():
    try:
        start_date, end_date = parse_args(request.args)
        db = db_context.get_db()
        res = db.get_unique_users(start_date, end_date)
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/views-per-week')
def get_views_per_week():
    try:
        start_date, end_date = parse_args(request.args)
        db = db_context.get_db()
        res = db.get_views(start_date, end_date)
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/countries')
def get_countries():
    try:
        start_date, end_date = parse_args(request.args)
        db = db_context.get_db()
        res = db.get_countries(start_date, end_date, 'USER')
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/cities')
def get_cities():
    try:
        start_date, end_date = parse_args(request.args)
        db = db_context.get_db()
        res = db.get_cities(start_date, end_date, 'USER')
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/urls')
def get_urls():
    try:
        start_date, end_date = parse_args(request.args)
        db = db_context.get_db()
        res = db.get_urls(start_date, end_date, 'USER')
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/hostnames')
def get_hostnames():
    try:
        start_date, end_date = parse_args(request.args)
        db = db_context.get_db()
        res = db.get_hostnames(start_date, end_date, 'BOT')
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)
