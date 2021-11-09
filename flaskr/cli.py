import click
import pathlib
from flask import current_app
from flask.cli import with_appcontext
from flaskr.database import db
import flaskr.api.traffic_api as traffic_api
"""Flask CLI commands."""


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Drop existing database and create new one via SQL-Alchemy."""
    db.drop_all()
    db.create_all()
    current_app.logger.info('Initialized the database.')


@click.command('run-import')
@click.argument('logfile', type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=pathlib.Path))
@with_appcontext
def run_import_command(logfile: pathlib.Path):
    """For temporary development usage only!"""
    traffic_api.run_import(logfile)


@click.command('process-data')
@with_appcontext
def process_data():
    traffic_api.process_data()


@click.command('debug-noodling')
@with_appcontext
def debug_noodling():
    import datetime as dt
    import flaskr.processing.queries as queries
    start = dt.datetime(2020, 4, 1)
    end = dt.datetime(2020, 5, 1)
    is_bot = False

    print(queries.get_users(start, end, is_bot))
    print(queries.get_views(start, end, is_bot))
    print(queries.get_countries(start, end, is_bot))
    print(queries.get_cities(start, end, is_bot))
    print(queries.get_urls(start, end, is_bot))
    print(queries.get_hostnames(start, end, is_bot))
