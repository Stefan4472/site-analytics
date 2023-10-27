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


@blueprint.route("", methods=["POST"])
@login_required
def report_traffic():
    try:
        contract = ReportTrafficContract.load(request.json)
        store_traffic(contract)
        return Response(status=200)
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response="Invalid parameters: {}".format(e))


# TODO: needs a better name
def store_traffic(contract: ReportTrafficContract):
    contract.user_agent = contract.user_agent.strip()
    # Write to log.
    # TODO: use proper CSV library. Also, create a new file each day or every x records.
    with open(current_app.config["LOG_PATH"], "a") as log_file:
        log_file.write(
            f"{contract.timestamp},{contract.url},{contract.ip_address},{contract.user_agent}\n"
        )

    db.session.add(
        RawView(
            url=contract.url.strip(),
            ip_address=contract.ip_address.strip(),
            user_agent=contract.user_agent.strip(),
            timestamp=contract.timestamp,
        )
    )
    db.session.commit()
