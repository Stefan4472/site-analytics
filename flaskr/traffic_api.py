import datetime
from flask import Blueprint, current_app, request, Response
from flask_login import login_required
from flaskr import db
from models.user import User
from models.view import View
'''
TODO: SEND A 'WEEKLY REPORT' EMAIL? (Or move that to a different service?)

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


# Create blueprint, which will be used to register URL routes
blueprint = Blueprint('traffic', __name__, url_prefix='/api/v1/traffic')


@blueprint.route('', methods=['POST'])
@login_required
def report_traffic():
    # Ensure all other args are present
    if 'url' not in request.json:
        return Response('Missing "url" arg', status=400)
    if 'ip_addr' not in request.json:
        return Response('Missing "ip_addr" arg', status=400)
    if 'user_agent' not in request.json:
        return Response('Missing "user_agent" arg', status=400)

    # TODO: THESE STRINGS NEED TO BE ESCAPED
    url = request.json['url']
    user_ip = request.json['ip_addr']
    user_agent = request.json['user_agent']
    request_time = datetime.datetime.now()

    # Write to log file
    with open(current_app.config['LOG_PATH'], 'a') as log_file:
        log_file.write('{},{},{},{}\n'.format(
            request_time,
            url,
            user_ip,
            user_agent,
        ))

    # Add to database
    user = get_or_create_user(user_ip)
    view = View(url=url, user_agent=user_agent, timestamp=request_time)
    db.session.add(user)
    db.session.add(view)
    user.views.append(view)
    db.session.commit()

    return Response(status=200)


def get_or_create_user(ip_address: str) -> User:
    existing_user = User.query.filter_by(ip_address=ip_address).first()
    return existing_user if existing_user else User(ip_address=ip_address)


def process_users():
    for user in User.query.filter_by(was_processed=False):
        print(user)
        user.process()
    db.session.commit()


def run_import():
    with open('../log-test.txt') as f:
        for line in f:
            first_comma = line.index(',')
            second_comma = line.index(',', first_comma + 1)
            third_comma = line.index(',', second_comma + 1)

            timestamp = line[:first_comma]
            request_time = datetime.datetime.strptime(timestamp, '%m-%d-%Y-%H:%M:%S:%f')
            url = line[first_comma + 1:second_comma]
            ip = line[second_comma + 1:third_comma]
            user_agent = line[third_comma + 1:]

            print(timestamp)
            user = get_or_create_user(ip)
            view = View(url=url, user_agent=user_agent, timestamp=request_time)
            db.session.add(user)
            db.session.add(view)
            user.views.append(view)
    db.session.commit()
