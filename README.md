# site-analytics

A simple microservice for server-side storage and analysis of web traffic implemented with Python Flask. 

`site-analytics` uses the Timestamp, URL, IP address, and User Agent of requests. It uses the [FreeGeoIP API](https://freegeoip.app/) to geolocate IP addresses, and [the user-agents library](https://pypi.org/project/user-agents/) to parse User Agents. Data is stored in a PostgreSQL 13 instance.

# Setup

Install Postgres 13. We use `SQLAlchemy` along with the `psycopg2` library to access the database (these are included in the `requirements.txt`).

Install the required packages:
```
pip install -r requirements.txt
```

Create a postgres database to use. I recommend calling it `siteanalytics`
```
# Execute in psql, for example
CREATE DATABASE siteanalytics;
```

Setup a `.flaskenv` configuration file. The values you set here will automatically be stored as environment variables when you run Flask, and will be used to configure the website. In the `flaskr` folder, create a simple file called `.flaskenv` and enter the following:
```
FLASK_APP=.
FLASK_ENV=development
SECRET_KEY=<YOUR SECRET KEY HERE>
POSTGRES_USERNAME=<POSTGRES USERNAME TO USE>
POSTGRES_PASSWORD=<PASSWORD FOR POSTGRES USERNAME>
POSTGRES_HOST=<POSTGRES HOST, e.g. 127.0.0.1>
POSTGRES_PORT=<POSTGRES PORT>
POSTGRES_DATABASE_NAME=<NAME OF POSTGRES DATABASE YOU CREATED>
```

Make sure to set your secret key to something... secret. It will be used to authenticate API calls.


Now initialize the database tables:
```
flask init-db
```

Run the server:
```
flask run
```

The values you set in the `.flaskenv` will automatically be used to configure the server.

# Usage

All API calls must provide a header value called `Authorization` set to the secret key.

## Recording web traffic

Use the `/api/v1/traffic` endpoint to record web traffic.
```
requests.post(
    'http://127.0.0.1:5000/api/v1/traffic', 
    headers={'Authorization': 'dev'},
    params={
        'url': '/', 
        'ip_addr': '127.0.0.1', 
        'user_agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
        'timestamp': '2022-03-22T11:10:29.169057'  # ISO8601 format, i.e. datetime.isoformat()
    }
)
```

## Getting statistics data

Use the `/api/v1/data/statistics` endpoint to execute queries.

`site-analytics` provides a flexible interface for formulating queries. You must specify:
- `query_on`: Define whether you want to query "People" or "Bots"
- `count_what`: Define what you want to count: "Users" (unique IP addresses) or "Views" (number of requests)
- `group_what`: Define how you want to categorize the results, e.g. by "Country", "City", "Url", or "Browser". It also supports several other categories. 
- `resolution`: Define the time period with which to bin the results, e.g. "AllTime", "Day", "Week", "Month" or "Year"
- `start_date` (optional, 'MM-DD-YYYY'): Define the start date of the query. Only requests timestamped on `start_date` or later will be considered in the query.
- `end_date` (optional, 'MM-DD-YYYY'): Define the end date of the query. Only requests timestamped before `end_date` will be considered in the query.

For example:
```
# Get the total number of views by bots, grouped by country, between 4/1/2020 and 3/13/2022.
GET /api/v1/data/statistics?query_on=Bots&count_what=Views&group_what=Country&resolution=All&start_date=04-01-2020&end_date=03-13-2022
```

See `flaskr/processing/query_runner.py` for all queryable properties.