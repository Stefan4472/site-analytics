import typing
import datetime
import pathlib
from flask import Blueprint, g, request, Response
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
# A session is defined by a user



# Create blueprint, which will be used to register URL routes
blueprint = Blueprint('backend', __name__)

# A simple page that says hello
@blueprint.route('/hello')
def hello():
    user_ip = request.environ.get(
        'HTTP_X_FORWARDED_FOR', request.environ['REMOTE_ADDR']
    )
    db = database_context.get_db()
    user = db.get_user(user_ip)
    if not user:
        print('Creating user')
        user = db.create_user(user_ip)
        db.commit()
    print(user)
    return 'Hello, World!'

"""
app.config['next_session_id'] = 1
app.config['active_sessions_by_ip'] = {}
app.config['db'] = database.Database('views.db')  # TODO: MOVE TO 'INSTANCE' FOLDER

# next_session_id = 1
# Active sessions, indexed by IP address
# active_sessions_by_ip: typing.Dict[str, session.Session] = {}
# TODO: NEED TO REMOVE AFTER X MINUTES OF INACTIVITY. INACTIVE_TIMER?

# def create_session(  TODO


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