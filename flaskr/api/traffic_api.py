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
from flask import Blueprint, current_app, request, Response
from flask_login import login_required
from flaskr import db
from flaskr.models.user import User
from flaskr.models.view import View
from flaskr.contracts.report_traffic import ReportTrafficContract
# TODO: SEND A 'WEEKLY REPORT' EMAIL?
# Note: Users are uniquely defined by their IP address.
# TODO: DEFINE BY (IP_ADDRESS, USER_AGENT)?


blueprint = Blueprint('traffic', __name__, url_prefix='/api/v1/traffic')


@blueprint.route('', methods=['POST'])
@login_required
def report_traffic():
    try:
        contract = ReportTrafficContract.load(request.json)
        store_traffic(contract)
        return Response(status=200)
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))


def get_or_create_user(ip_address: str) -> User:
    existing_user = User.query.filter_by(ip_address=ip_address).first()
    return existing_user if existing_user else User(ip_address=ip_address)


def store_traffic(contract: ReportTrafficContract):
    contract.user_agent = contract.user_agent.strip()
    # Write to log
    with open(current_app.config['LOG_PATH'], 'a') as log_file:
        log_file.write(f'{contract.timestamp},{contract.url},{contract.ip_address},{contract.user_agent}\n')

    # Add to database. SQL-Alchemy will escape strings before processing them.
    user = get_or_create_user(contract.ip_address)
    view = View(contract.url, contract.user_agent, contract.timestamp)
    db.session.add(user)
    db.session.add(view)
    user.my_views.append(view)
    db.session.commit()
