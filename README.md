# site-analytics
An API to record a website's traffic implemented in Python Flask. Python 3.6

# Setup

Install the "analyticsdb" package:
```
cd analyticsdb
pip install -e .
```

Install the required packages for the Flask instance:
```
cd flaskr
pip install flask
pip install dataclasses
```

TODO: Setup database with the schema

Run Flask:
```
cd flaskr
set FLASK_APP=.
set FLASK_ENV=development
flask run
```

# Steps
Try: "127.0.0.1:5000/query?secret=0JkoHv55RSrc7MwpV0wR&start_date=2020-10-1&end_date=2020-11-10&interval=5"

# Possible additions
Support multiple API keys.
Require authentication via API key.