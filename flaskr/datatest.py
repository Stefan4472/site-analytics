import datetime as dt
import flaskr.queries as queries


def run():
    print('Yo')
    start = dt.datetime(2020, 4, 1)
    end = dt.datetime(2020, 5, 1)

    """Number of unique IP addresses by-user and by-bot, per week."""
    queries.get_users(start, end, False)
    queries.get_views(start, end, False)
    queries.get_countries(start, end, False)
    queries.get_cities(start, end, False)
    queries.get_urls(start, end, False)
    queries.get_hostnames(start, end, False)
