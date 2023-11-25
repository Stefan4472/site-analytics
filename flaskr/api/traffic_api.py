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
from flask import Blueprint, Response, request
from flask_login import login_required

from flaskr.contracts.report_traffic import ReportTrafficContract
from flaskr.storage.raw_view_storage import write_raw_views

blueprint = Blueprint("traffic", __name__, url_prefix="/api/v1/traffic")


# The maximum number of views allowed to be reported per request.
MAX_ALLOWED_VIEWS_PER_REQUEST = 200


@blueprint.route("", methods=["POST"])
@login_required
def report_traffic():
    try:
        contract = ReportTrafficContract.load(request.json)
        if not contract.views:
            return Response(
                status=400, response="The request did not contain any traffic records."
            )
        if len(contract.views) > MAX_ALLOWED_VIEWS_PER_REQUEST:
            return Response(
                status=400,
                response=f"Too many traffic records in this request; the maximum "
                f"allowed is {MAX_ALLOWED_VIEWS_PER_REQUEST} but this one"
                f" has {len(contract.views)}",
            )
        write_raw_views(contract.views)
        return Response(status=200)
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response=f"Invalid parameters: {e}")
