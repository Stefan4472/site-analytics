import datetime as dt
import flaskr.processing.queries as queries


def run():
    start = dt.datetime(2020, 4, 1)
    end = dt.datetime(2020, 5, 1)
    is_bot = False

    print(queries.get_users(start, end, is_bot))
    print(queries.get_views(start, end, is_bot))
    print(queries.get_countries(start, end, is_bot))
    print(queries.get_cities(start, end, is_bot))
    print(queries.get_urls(start, end, is_bot))
    print(queries.get_hostnames(start, end, is_bot))
