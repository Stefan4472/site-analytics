from flask import Flask, request, Response
import typing
import session
import datetime


app = Flask(__name__)
app.config['next_session_id'] = 1
app.config['active_sessions_by_ip'] = {}
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

@app.route('/', methods=['GET'])
def hello_world():
    return Response(status=200)

# TODO: AUTHENTICATION, 'USER KEYS'
# FOR NOW, JUST GET THIS LOGGING TRAFFIC TO A FILE
@app.route('/report_traffic', methods=['POST'])
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

    # Return success
    return Response(status=200)

# TODO: DEBUGGING ONLY
if __name__ == "__main__":
    app.run(port=5001)
