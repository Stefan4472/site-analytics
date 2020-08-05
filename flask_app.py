from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return Response(status=200)

# TODO: AUTHENTICATION, 'USER KEYS'
@app.route('/report_traffic', methods=['POST'])
def report_traffic():
    url = request.args['url']
    ip_addr = request.args['ip_addr']
    user_agent = request.args['user_agent']
    print('Got "report_traffic" with args "{}", "{}", "{}"'.format(
        url, ip_addr, user_agent))
    # Return error if parameters haven't been specified
    if not (url and ip_addr and user_agent):
        return Response(status=400)
       
    return Response(status=200)

# TODO: DEBUGGING ONLY
if __name__ == "__main__":
    app.run(port=5001)
