import datetime
from flask import Blueprint, current_app, request, Response
from flask_login import login_required
from analyticsdb import user as us
from analyticsdb import session as se
from . import database_context
from . import hostname_lookup
from . import location_lookup
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


def get_or_create_user(
        ip_address: str,
) -> us.User:
    db = database_context.get_db()
    user = db.get_user(ip_address)
    return user if user else db.create_user(ip_address, commit=True)


def get_or_create_session(
        user: us.User,
        request_time: datetime.datetime,
) -> se.Session:
    # Check if user has a cached session
    db = database_context.get_db()
    cached_session = db.lookup_cached_session(user.user_id)
    # Session is active: use it
    if cached_session and cached_session.is_active():
        return cached_session
    # Session is now inactive: mark it as stale and create new session
    elif cached_session:
        db.update_cached_session(cached_session, is_stale=True)
        session = db.create_session(user, request_time)
        db.add_session_to_cache(session)
        db.commit()
        return session
    else:
        session = db.create_session(user, request_time)
        db.add_session_to_cache(session)
        db.commit()
        return session


def process_user(
        user: us.User,
        session: se.Session,
) -> us.User:
    hostname = hostname_lookup.hostname_from_ip(user.ip_address)
    location = location_lookup.location_from_ip(user.ip_address)

    user.hostname = hostname
    user.domain = hostname_lookup.domain_from_hostname(hostname)
    user.city = location.city
    user.region = location.region_name
    user.country = location.country_name
    user.classification = us.classify_user(user, session)
    user.was_processed = True
    return user  # TODO: DO WE NEED TO RETURN IT?


def process_cached_sessions():
    db = database_context.get_db()
    i = 0
    for session in db.gen_all_cached_sessions():
        i += 1
        if i >= 10000:
            print(i)
            # Get associated user
            user = db.get_user_by_id(session.user_id)
            if not user.was_processed:
                user = process_user(user, session)
                db.update_user(user)
    db.commit()


def run_import():
    with open('../log.txt') as f:
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
            session = get_or_create_session(user, request_time)
            session.record_request(request_time)
            # Record the view and update the session
            db = database_context.get_db()
            db.record_view(session, request_time, url, user_agent)
            db.update_session(session)
    db.commit()


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

    url = request.json['url']
    user_ip = request.json['ip_addr']
    user_agent = request.json['user_agent']
    request_time = datetime.datetime.strptime(request.json['timestamp'], '%m-%d-%Y-%H:%M:%S:%f')
    # request_time = datetime.datetime.now()

    # TODO: THESE STRINGS NEED TO BE ESCAPED BEFORE WRITING TO DATABASE
    # Write to log file
    # with open(current_app.config['LOG_PATH'], 'a') as log_file:
    #     log_file.write('{},{},{},{}\n'.format(
    #         request_time,
    #         url,
    #         user_ip,
    #         user_agent,
    #     ))

    user = get_or_create_user(user_ip)
    session = get_or_create_session(user, request_time)
    session.record_request(request_time)

    # Record the view and update the session
    db = database_context.get_db()
    db.record_view(session, request_time, url, user_agent)
    db.update_session(session)
    db.commit()

    return Response(status=200)
