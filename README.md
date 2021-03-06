# site-analytics

An API used to record a website's traffic and analyze the results. Implemented with Python 3.6 Flask.

# Overview

Let's say that you run a website. You want to be able to track statistics about your website, such as how many hits it's receiving, which URLs are popular, where traffic is coming from geographically, etc.

This project provides a microservice that your website can use to record traffic and later analyze it. Your website sends the IP address and user agent of each request it receives, as well as the URl requested, to the analytics webserver. The analytics webserver processes and stores this data, drawing meaningful conclusions from it. You can then use the data API to calculate metrics on your site's traffic.

The analytics webserver tracks users via unique IP addresses. It tracks user sessions, and uses the IP addresses to determine rough geolocations. This allows it to often determine the country and city from which the request is coming from. It also detects bots and distinguishes between user activity and bot activity.

This API is functional, but waiting for some cleanup and improved functionality.

# Setup

Install the "analyticsdb" package:
```
# in the `analyticsdb` folder
pip install -e .
```

Install the required packages for the Flask instance:
```
# in the `flaskr` folder
pip install flask
pip install flask-login
pip install dataclasses
```

Setup Flask:
```
# in the `flaskr` folder
set FLASK_APP=.
set FLASK_ENV=development
```

Add your secret key. This will be used to authenticate API calls:
- Go to the `flaskr` folder
- Create a new directory called `instance`
- Create a new file in `instance` called `secret.txt`
- Write your secret key into the file. No whitespace or linebreaks.

Create the database instance using the schema defined in `analyticsdb`:
```
# in the `flaskr` folder
flask init-db ../analyticsdb/schema.sql
```

Run the server:
```
flask run
```

# Usage

**NOTE**: All API calls must provide a header value called `Authorization`, with the value of the secret key. For example, using the `requests` module in Python:
```
requests.get(
    'http://127.0.0.1:5000/api/v1/data/unique-ips-per-week',
    headers={'Authorization': 'dev'},
    params={'start_date': '2020-10-10', 'end_date': '2021-3-15'},
)
```

## Traffic recording

The website that you are recording traffic for will use the `/api/v1/traffic` POST endpoint, and provide the URL being requested, the IP address of the request, and the user agent of the request. For example, using the `requests` module in Python:
```
params = {'url': '/', 'ip_addr': '127.0.0.1', 'user_agent': 'Firefox'}
r = requests.post(
    'http://127.0.0.1:5000/api/v1/traffic', 
    headers={'Authorization': 'dev'},
    params={'url': '/', 'ip_addr': '127.0.0.1', 'user_agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.92 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'},
)
```

## Data analysis

The following endpoints are provided:
- `/api/v1/data/unique-ips-per-week` (start_date, end_date)
- `/api/v1/data/views-per-week` (start_date, end_date)
- `/api/v1/data/countries` (start_date, end_date, classification)
- `/api/v1/data/cities` (start_date, end_date, classification)
- `/api/v1/data/urls` (start_date, end_date, classification)
- `/api/v1/data/hostnames` (start_date, end_date, classification)

`start_date` and `end_date` provide the date range for the queries. These must be in the format `YYYY-MM-DD`. `classification` must be either `USER` OR `BOT`.
