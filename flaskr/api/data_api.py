# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import marshmallow
from flask import Blueprint, Response, jsonify, request
from flask_login import login_required

from flaskr.contracts.data_request import DataRequestContract
from flaskr.database import db
from flaskr.processing.query_runner import QueryRunner

# TODO: SETUP AUTO-SWAGGER DOCUMENTATION USING MARSHMALLOW DEFINITIONS?


blueprint = Blueprint("data", __name__, url_prefix="/api/v1/data")


@blueprint.route("/statistics")
@login_required
def statistics():
    try:
        contract = DataRequestContract.load(request.args)
        return jsonify(QueryRunner.run_query(contract.to_query(), db.session))
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response="Invalid parameters: {}".format(e))
