import marshmallow
from flask import Blueprint, request, Response, jsonify
from flask_login import login_required
import flaskr.processing.queries as queries
from flaskr.contracts.data_request import DataRequestContract
# TODO: SETUP AUTO-SWAGGER DOCUMENTATION USING MARSHMALLOW DEFINITIONS


# Create blueprint, which will be used to register URL routes
blueprint = Blueprint('data', __name__, url_prefix='/api/v1/data')


@blueprint.route('/users')
@login_required
def get_users():
    """Query on number of unique users."""
    try:
        contract: DataRequestContract = DataRequestContract.get_schema().load(request.args)
        res = queries.get_users(contract.start_date, contract.end_date, contract.classification)
        return jsonify(res)
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))


@blueprint.route('/views')
@login_required
def get_views():
    """Query on number of views."""
    try:
        contract: DataRequestContract = DataRequestContract.get_schema().load(request.args)
        res = queries.get_views(contract.start_date, contract.end_date, contract.classification)
        return jsonify(res)
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))


# TODO: COMBINE INTO ONE 'LOCATION' ENDPOINT? OR ADD AS SELECTION PARAMS ON USER AND VIEW ENDPOINTS?
@blueprint.route('/countries')
@login_required
def get_countries():
    """Query on number of views per country."""
    try:
        contract: DataRequestContract = DataRequestContract.get_schema().load(request.args)
        res = queries.get_countries(contract.start_date, contract.end_date, contract.classification)
        return jsonify(res)
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))


@blueprint.route('/cities')
@login_required
def get_cities():
    """Query on number of views per city."""
    try:
        contract: DataRequestContract = DataRequestContract.get_schema().load(request.args)
        res = queries.get_cities(contract.start_date, contract.end_date, contract.classification)
        return jsonify(res)
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))


@blueprint.route('/urls')
@login_required
def get_urls():
    """Query on number of views per URL."""
    try:
        contract: DataRequestContract = DataRequestContract.get_schema().load(request.args)
        res = queries.get_urls(contract.start_date, contract.end_date, contract.classification)
        return jsonify(res)
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))


# TODO: PERHAPS COMBINE INTO THE /USERS ENDPOINT
@blueprint.route('/hostnames')
@login_required
def get_hostnames():
    """Query on number of views by hostname."""
    try:
        contract: DataRequestContract = DataRequestContract.get_schema().load(request.args)
        res = queries.get_hostnames(contract.start_date, contract.end_date, contract.classification)
        return jsonify(res)
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))
