from flask import Blueprint, request, Response, jsonify
from flask_login import login_required
from . import database_context as db_context
from . import argparser


# Create blueprint, which will be used to register URL routes
blueprint = Blueprint('data', __name__, url_prefix='/api/v1/data')


# TODO: MAKE INTERVALS OPTIONAL AND VARIABLE
@blueprint.route('/unique-ips-per-week')
@login_required
def get_unique_ips_per_week():
    """Number of unique IP addresses by-user and by-bot, per week."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
        )
        db = db_context.get_db()
        res = db.get_unique_ips(args.start_date, args.end_date)
        return jsonify(res)
    except argparser.ParseException as e:
        return Response(str(e), status=400)


@blueprint.route('/views-per-week')
@login_required
def get_views_per_week():
    """Number of views by-user and by-bot, per week."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
        )
        db = db_context.get_db()
        res = db.get_views(args.start_date, args.end_date)
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/countries')
@login_required
def get_countries():
    """Views per country."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
            req_classification=True,
        )
        db = db_context.get_db()
        res = db.get_countries(args.start_date, args.end_date, args.classification)
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/cities')
@login_required
def get_cities():
    """Views per city."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
            req_classification=True,
        )
        db = db_context.get_db()
        res = db.get_cities(args.start_date, args.end_date, args.classification)
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/urls')
@login_required
def get_urls():
    """Views per URL."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
            req_classification=True,
        )
        db = db_context.get_db()
        res = db.get_urls(args.start_date, args.end_date, args.classification)
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/hostnames')
@login_required
def get_hostnames():
    """Views by hostname."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
            req_classification=True,
        )
        db = db_context.get_db()
        res = db.get_hostnames(args.start_date, args.end_date, args.classification)
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)
