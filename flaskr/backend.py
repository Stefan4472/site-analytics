import typing
import datetime
import pathlib
import json
from flask import Blueprint, g, current_app, request, Response, jsonify
from analyticsdb import database
from analyticsdb import user as us
from analyticsdb import session as se
from . import database_context
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
            db.update_user(user)
    db.commit()


@blueprint.route('/report_traffic', methods=['POST'])
def report_traffic():
    # Check 'secret' key
    if 'secret' not in request.args:
        return Response('Missing "secret" arg', status=400)
    if request.args['secret'] != current_app.config['SECRET_KEY']:
        return Response('Invalid "secret" key provided', status=403)

    # Ensure all other args are present
    if 'url' not in request.args:
        return Response('Missing "url" arg', status=400)
    if 'ip_addr' not in request.args:
        return Response('Missing "ip_addr" arg', status=400)
    if 'user_agent' not in request.args:
        return Response('Missing "user_agent" arg', status=400)

    url = request.args['url']
    user_ip = request.args['ip_addr']
    user_agent = request.args['user_agent']
    secret_key = request.args['secret']
    # TODO: TAKE TIMESTAMP
    request_time = datetime.datetime.now()

    print('Got "report_traffic" with args "{}", "{}", "{}", secret="{}"'.format(
            url, user_ip, user_agent, secret_key)
    )

    # TODO: THESE STRINGS NEED TO BE ESCAPED BEFORE WRITING TO DATABASE

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

    # Record the view and update the session
    db = database_context.get_db()
    db.record_view(session, request_time, url, user_agent)
    db.update_session(session)
    db.commit()

    return Response(status=200)


def parse_date(date_str: str) -> datetime.date:
    """Parses a string date in format YYYY-MM-DD."""
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


@blueprint.route('/query', methods=['GET'])
def query():
    """Execute simple query (early stage of development).

    Args required:
    - secret key ("secret")
    - start_date inclusive ("start_date", "YYYY-MM-DD")
    - end_date inclusive ("end_date", "YYYY-MM-DD")

    Optional args:
    - interval ("interval", [num days])
    """
    # Check 'secret' key
    if 'secret' not in request.args:
        return Response('Missing "secret" arg', status=400)
    if request.args['secret'] != current_app.config['SECRET_KEY']:
        return Response('Invalid "secret" key provided', status=403)

    # Ensure all other args are present
    if 'start_date' not in request.args:
        return Response('Missing "start_date" arg', status=400)
    start_date = parse_date(request.args['start_date'])
    if 'end_date' not in request.args:
        return Response('Missing "end_date" arg', status=400)
    end_date = parse_date(request.args['end_date'])
    
    db = database_context.get_db()

    # TODO: BETTER HANDLING OF DIFFERENCE
    if 'interval' in request.args:
        interval_days = int(request.args['interval'])
        json_results = []

        # TODO: FIGURE OUT HOW DATES TRANSLATE TO DATETIMES--i.e., MIDNIGHT ON WHICH DAY?
        # Query on each interval
        interval_start = start_date
        while interval_start < end_date:
            interval_end = interval_start + datetime.timedelta(
                days=interval_days,
            )
            if interval_end > end_date:
                interval_end = end_date

            num_hits = db.count_hits_in_range(
                interval_start,
                interval_end,
            )[0]

            json_results.append({
                'start_date': str(interval_start),
                'end_date': str(interval_end),
                'hits': num_hits,
            })
            
            interval_start = interval_end
        return json.dumps(json_results)
    else:
        num_hits = db.count_hits_in_range(
            start_date,
            end_date,
        )[0]

        return json.dumps({
            'start_date': str(start_date),
            'end_date': str(end_date),
            'hits': num_hits,
        })


@blueprint.route('/get')
def get_data():
    query = 'SELECT _classification, COUNT(*) FROM _Users GROUP BY _classification'
    res = database_context.get_db().cur.execute(query)
    _json = [{row[0]: row[1]} for row in res.fetchall()]
    return jsonify(_json)
