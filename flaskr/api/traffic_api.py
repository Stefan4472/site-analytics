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
from flask import Blueprint, Response, current_app, request
from flask_login import login_required

from flaskr import db
from flaskr.contracts.report_traffic import ReportTrafficContract
from flaskr.models.raw_view import RawView

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
        store_traffic(contract)
        return Response(status=200)
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response=f"Invalid parameters: {e}")


# TODO: needs a better name
def store_traffic(contract: ReportTrafficContract):
    for view in contract.views:
        # Write to log.
        # TODO: use proper CSV library. Also, create a new file each day or every x records.
        with open(current_app.config["LOG_PATH"], "a") as log_file:
            log_file.write(
                f"{view.timestamp},{view.url.strip()},{view.ip_address.strip()},{view.user_agent.strip()}\n"
            )

        db.session.add(
            RawView(
                url=view.url.strip(),
                ip_address=view.ip_address.strip(),
                user_agent=view.user_agent.strip(),
                timestamp=view.timestamp,
            )
        )
        db.session.commit()
