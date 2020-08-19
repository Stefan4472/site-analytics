import typing
import datetime
import pathlib
from flask import Blueprint, g, current_app, request, Response
from . import database
from . import database_context
from . import user
from . import session

# Plan of attack:
# 1. Get extremely simple 'post' API working that just logs traffic (as I had already done)
# 2. Record data to a simple SQLite database, rather than a .txt file
# 3. Implement tracking of sessions
# 4. Implement classifications of sessions
# 5. Implement plotting of analytics via API

# Currently, users are defined by their IP address.
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
) -> user.User:
    db = database_context.get_db()
    user = db.get_user(ip_address)
    if user:
        print('Found user')
        return user
    else:
        print('Creating user')
        return db.create_user(ip_address, commit=True)


def get_or_create_session(
        user: user.User,
        request_time: datetime.datetime,
) -> session.Session:
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

"""
def get_session(ip_addr: str):
    existing_session = app.config['active_sessions_by_ip'].get(ip_addr)
    # Create session
    if existing_session is None:
        print('Creating new session')
        new_session = session.Session(
            ip_addr, 
            session_id=app.config['next_session_id'],
        )
        app.config['next_session_id'] += 1
        app.config['active_sessions_by_ip'][ip_addr] = new_session
        return new_session
    # Session exists
    else:
        return existing_session

@blueprint.route('/', methods=['GET'])
def hello_world():
    return Response(status=200)

# TODO: AUTHENTICATION, 'USER KEYS'
# FOR NOW, JUST GET THIS LOGGING TRAFFIC TO A FILE
@blueprint.route('/report_traffic', methods=['POST'])
def report_traffic():
    url = request.args['url']
    ip_addr = request.args['ip_addr']
    user_agent = request.args['user_agent']
    # TODO: TAKE TIMESTAMP
    print('Got "report_traffic" with args "{}", "{}", "{}"'.format(
        url, ip_addr, user_agent))
    # Return error if parameters haven't been specified
    if not (url and ip_addr and user_agent):
        print('Error: missing required parameter(s)')
        return Response(status=400)
       
    session = get_session(ip_addr)
    print(session)

    # Write to log file
    with open('log.txt', 'a') as log_file:
        log_file.write('{},{},{},{}\n'.format(
            datetime.datetime.now(), 
            url, 
            ip_addr, 
            user_agent,
        ))

    # TODO: THESE STRINGS NEED TO BE CHECKED BEFORE WRITING TO DATABASE
    # Write to database
    app.config['db'].record_view(url, ip_addr, user_agent)

    # Return success
    return Response(status=200)
"""