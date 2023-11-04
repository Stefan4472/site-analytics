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
from datetime import datetime

import marshmallow
from flask import Blueprint, Response, jsonify, request
from flask_login import login_required

from flaskr.contracts.query_contract import QueryContract
from flaskr.database import db
from flaskr.processing.query_runner import Query, run_query

blueprint = Blueprint("data", __name__, url_prefix="/api/v1/data")


@blueprint.route("/query")
# @login_required
def query():
    """
    Endpoint used to execute a query against the ProcessedViews.
    Arguments are expected as query parameters.
    """
    try:
        print(request.args)
        query_ = QueryContract.load(request.args).to_query()
        res = run_query(db.session, query_)
        return [bucket.json() for bucket in res]
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response="Invalid parameters: {}".format(e))
