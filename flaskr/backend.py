import typing
import datetime
import pathlib
from flask import Blueprint, g, current_app, request, Response
from . import database
from . import database_context
from . import user as us
from . import session as se
from . import hostname_lookup
from . import location_lookup


# TODO: SEND A 'WEEKLY REPORT' EMAIL

# Currently, users are defined by their IP address.
# TODO: DEFINE BY (IP_ADDRESS, USER_AGENT)
# A session is defined by a user IP address and start time.
# Flow:
# - Look up IP address to get the user. Create new user if not exists
# - Look up user in `active_sessions`. Update active session if exists,
# else create and add to `active_sessions`
# - Create new View record, using the active session
# - Update `active_sessions`. For those that have expired, analyze them
# and save their updated values to the database. Use them to classify their
# corresponding users  


# Create blueprint, which will be used to register URL routes
blueprint = Blueprint('backend', __name__)


def get_or_create_user(
        ip_address: str,
) -> us.User:
    db = database_context.get_db()
    user = db.get_user(ip_address)
    if user:
        print('Found user')
        return user
    else:
        print('Creating user')
        return db.create_user(ip_address, commit=True)


def get_or_create_session(
        user: us.User,
        request_time: datetime.datetime,
) -> se.Session:
    # Check if user has a cached session
    db = database_context.get_db()
    cached_session = db.lookup_cached_session(user.user_id)
    print('Found cached session {}'.format(cached_session))
    # Session is active: use it
    if cached_session and cached_session.is_active():
        print('Found active cached session')
        return cached_session
    # Session is now inactive: mark it as stale and create new session
    elif cached_session:
        print('Found inactive cached session: marking stale and creating new session')
        db.update_cached_session(cached_session, is_stale=True)
        session = db.create_session(user, request_time)
        db.add_session_to_cache(session)
        db.commit()
        return session
    else:
        print('Didn\'t find cached session: creating a new one')
        session = db.create_session(user, request_time)
        db.add_session_to_cache(session)
        db.commit()
        return session


def process_user(
        user: us.User,
        session: se.Session,
) -> us.User:
    print('Processing user with id {}'.format(user.user_id))
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
    for session in db.gen_all_cached_sessions():
        # Get associated user
        user = db.get_user_by_id(session.user_id)
        if not user.was_processed:
            user = process_user(user, session)
            print(user)
            db.update_user(user)
    db.commit()


# A simple page that says hello
@blueprint.route('/hello')
def hello():
    user_ip = request.environ.get(
        'HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR']
    )
    request_time = datetime.datetime.now()
    url = '/hello'
    user_agent = 'firefox'

    user = get_or_create_user(user_ip)
    session = get_or_create_session(user, request_time)
    session.record_request(request_time)

    print(user)
    print(session)

    # Record the view and update the session
    db = database_context.get_db()
    db.record_view(session, request_time, url, user_agent)
    db.update_session(session)
    db.commit()

    all_cached = db.cur.execute('select * from _CachedSessions').fetchall()
    for c in all_cached:
        print(*c)
    print()
    return 'Hello, World!'

# TODO: AUTHENTICATION, 'USER KEYS'
@blueprint.route('/report_traffic', methods=['POST'])
def report_traffic():
    url = request.args['url']
    user_ip = request.args['ip_addr']
    user_agent = request.args['user_agent']
    # TODO: TAKE TIMESTAMP
    request_time = datetime.datetime.now()

    print('Got "report_traffic" with args "{}", "{}", "{}"'.format(
            url, user_ip, user_agent)
    )

    # TODO: THESE STRINGS NEED TO BE CHECKED BEFORE WRITING TO DATABASE

    # Return error if parameters haven't been specified
    if not (url and user_ip and user_agent):
        print('Error: missing required parameter(s)')
        return Response(status=400)

    # Write to log file
    with open(current_app.config['LOG_PATH'], 'a') as log_file:
        log_file.write('{},{},{},{}\n'.format(
            request_time, 
            url, 
            user_ip, 
            user_agent,
        ))

    user = get_or_create_user(user_ip)
    session = get_or_create_session(user, request_time)
    session.record_request(request_time)

    print(user)
    print(session)

    # Record the view and update the session
    db = database_context.get_db()
    db.record_view(session, request_time, url, user_agent)
    db.update_session(session)
    db.commit()

    for view_record in db.cur.execute('select * from _Views').fetchall():
        print(*view_record)
    print()
    return Response(status=200)
