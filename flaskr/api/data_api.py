from flask import Blueprint, request, Response, jsonify
from flask_login import login_required
from flaskr.api import argparser
import flaskr.processing.queries as queries
# TODO: USE MARSHMALLOW TO PARSE CONTRACTS AND SETUP AUTO-SWAGGER DOCUMENTATION


# Create blueprint, which will be used to register URL routes
blueprint = Blueprint('data', __name__, url_prefix='/api/v1/data')


@blueprint.route('/users')
@login_required
def get_users():
    """Query on number of unique users."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
        )
        res = queries.get_users(args.start_date, args.end_date, args.classification.is_bot())
        return jsonify(res)
    except argparser.ParseException as e:
        return Response(str(e), status=400)


@blueprint.route('/views')
@login_required
def get_views():
    """Query on number of views."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
        )
        res = queries.get_views(args.start_date, args.end_date, args.classification.is_bot())
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


# TODO: COMBINE INTO ONE 'LOCATION' ENDPOINT? OR ADD AS SELECTION PARAMS ON USER AND VIEW ENDPOINTS?
@blueprint.route('/countries')
@login_required
def get_countries():
    """Query on number of views per country."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
            req_classification=True,
        )
        res = queries.get_countries(args.start_date, args.end_date, args.classification.is_bot())
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/cities')
@login_required
def get_cities():
    """Query on number of views per city."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
            req_classification=True,
        )
        res = queries.get_cities(args.start_date, args.end_date, args.classification.is_bot())
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


@blueprint.route('/urls')
@login_required
def get_urls():
    """Query on number of views per URL."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
            req_classification=True,
        )
        res = queries.get_urls(args.start_date, args.end_date, args.classification.is_bot())
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)


# TODO: PERHAPS COMBINE INTO THE /USERS ENDPOINT
@blueprint.route('/hostnames')
@login_required
def get_hostnames():
    """Query on number of views by hostname."""
    try:
        args = argparser.parse_args(
            request.args,
            req_start_date=True,
            req_end_date=True,
            req_classification=True,
        )
        res = queries.get_hostnames(args.start_date, args.end_date, args.classification.is_bot())
        return jsonify(res)
    except ValueError as e:
        return Response(str(e), status=400)
