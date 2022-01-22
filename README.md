# site-analytics

An API used to record a website's traffic and analyze the results. Implemented with Python 3.6 using Flask and PostgreSQL13.

# Overview

Let's say that you run a website. You want to be able to track statistics about your website, such as how many hits it's receiving, which URLs are popular, where traffic is coming from geographically, etc.

This project provides a microservice that your website can use to record traffic and later analyze it. Your website sends the IP address and user agent of each request it receives, as well as the URl requested, to the analytics webserver. The analytics webserver processes and stores this data, drawing meaningful conclusions from it. You can then use the data API to calculate metrics on your site's traffic.

The analytics webserver tracks users via unique IP addresses. It tracks user sessions, and uses the IP addresses to determine rough geolocations. This allows it to often determine the country and city from which the request is coming from. It also detects bots and distinguishes between user activity and bot activity.

This API is functional, but waiting for some cleanup and improved functionality.

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


Now create the database instance:
```
flask init-db
```

Run the server:
```
flask run
```

The values you set in the `.flaskenv` will automatically be used to configure the server.

# Usage

**NOTE**: All API calls must provide a header value called `Authorization`, with the value of the secret key. For example, using the `requests` module in Python:
```
requests.get(
    'http://127.0.0.1:5000/api/v1/data/users',
    headers={'Authorization': '<YOUR SECRET KEY>'},
    params={'start_date': '2020-10-10', 'end_date': '2021-3-15'},
)
```

## Traffic recording

The website that you are recording traffic for will use the `/api/v1/traffic` POST endpoint, and provide the URL being requested, the IP address of the request, and the user agent of the request. For example, using the `requests` module in Python:
```
r = requests.post(
    'http://127.0.0.1:5000/api/v1/traffic', 
    headers={'Authorization': 'dev'},
    params={'url': '/', 'ip_addr': '127.0.0.1', 'user_agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.92 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'},
)
```

## Data analysis

The following endpoints are provided:
- `/api/v1/data/users` (start_date, end_date)
- `/api/v1/data/views` (start_date, end_date)
- `/api/v1/data/countries` (start_date, end_date, classification)
- `/api/v1/data/cities` (start_date, end_date, classification)
- `/api/v1/data/urls` (start_date, end_date, classification)
- `/api/v1/data/hostnames` (start_date, end_date, classification)

`start_date` and `end_date` provide the date range for the queries. These must be in the format `YYYY-MM-DD`. `classification` must be either `USER` OR `BOT`.
