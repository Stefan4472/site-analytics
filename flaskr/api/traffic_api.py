import datetime
import pathlib
import time
import marshmallow
from flask import Blueprint, current_app, request, Response
from flask_login import login_required
from flaskr import db
from flaskr.models.user import User
from flaskr.models.view import View
from flaskr.contracts.report_traffic import ReportTrafficContract
'''
TODO: SEND A 'WEEKLY REPORT' EMAIL?

Currently, users are defined by their IP address.
TODO: DEFINE BY (IP_ADDRESS, USER_AGENT)
A session is defined by a user IP address and start time.
Flow:
- Look up IP address to get the user. Create new user if not exists
- Look up user in `active_sessions`. Update active session if exists,
else create and add to `active_sessions`
- Create new View record, using the active session
- Update `active_sessions`. For those that have expired, analyze them
and save their updated values to the database. Use them to classify their
corresponding users  
'''


blueprint = Blueprint('traffic', __name__, url_prefix='/api/v1/traffic')


@blueprint.route('', methods=['POST'])
@login_required
def report_traffic():
    try:
        contract: ReportTrafficContract = ReportTrafficContract.get_schema().load(request.json)
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    request_time = datetime.datetime.now()
    # Write to log file
    with open(current_app.config['LOG_PATH'], 'a') as log_file:
        log_file.write('{},{},{},{}\n'.format(
            request_time,
            contract.url,
            contract.ip_address,
            contract.user_agent,
        ))

    # Add to database. SQL-Alchemy will escape strings before processing them.
    user = get_or_create_user(contract.ip_address)
    view = View(url=contract.url, user_agent=contract.user_agent, timestamp=request_time)
    view.process()
    db.session.add(user)
    db.session.add(view)
    user.views.append(view)
    db.session.commit()

    return Response(status=200)


def get_or_create_user(ip_address: str) -> User:
    existing_user = User.query.filter_by(ip_address=ip_address).first()
    return existing_user if existing_user else User(ip_address=ip_address)


def process_data():
    current_app.logger.info('Running data processing')
    i = 0
    for user in User.query.filter_by(was_processed=False):
        time.sleep(0.5)
        try:
            user.process()
        except ValueError as e:
            current_app.logger.warning('Failure processing user {}: {}'.format(user.id, e.args))
        i += 1
        if i % 20 == 0:
            db.session.commit()
    db.session.commit()


# TODO: move this into its own script
def run_import(logfile: pathlib.Path):
    current_app.logger.info('Running import on logfile {}'.format(logfile.absolute()))
    with open(logfile) as f:
        i = 0
        for line in f:
            i += 1
            if i > 1000:
                break
            first_comma = line.index(',')
            second_comma = line.index(',', first_comma + 1)
            third_comma = line.index(',', second_comma + 1)

            timestamp = line[:first_comma]
            request_time = datetime.datetime.strptime(timestamp, '%m-%d-%Y-%H:%M:%S:%f')
            url = line[first_comma + 1:second_comma]
            ip = line[second_comma + 1:third_comma]
            user_agent = line[third_comma + 1:]

            current_app.logger.info('Processed request with time {}'.format(timestamp))
            user = get_or_create_user(ip)
            view = View(url=url, user_agent=user_agent, timestamp=request_time)
            view.process()
            db.session.add(user)
            db.session.add(view)  # TODO: might be unnecessary
            user.views.append(view)
    db.session.commit()
