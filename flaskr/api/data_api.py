import marshmallow
from flask import Blueprint, request, Response, jsonify
from flask_login import login_required
from flaskr.database import db
from flaskr.processing.query_runner import QueryRunner
from flaskr.contracts.data_request import DataRequestContract
# TODO: SETUP AUTO-SWAGGER DOCUMENTATION USING MARSHMALLOW DEFINITIONS?


blueprint = Blueprint('data', __name__, url_prefix='/api/v1/data')


@blueprint.route('/statistics')
@login_required
def statistics():
    try:
        contract = DataRequestContract.load(request.args)
        return jsonify(QueryRunner.run_query(contract.to_query(), db.session))
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))
