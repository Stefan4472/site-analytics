import click
import pathlib
import sqlalchemy
from flask import current_app
from flask.cli import with_appcontext
from flaskr.database import db
import flaskr.api.traffic_api as traffic_api
"""Flask CLI commands."""


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create tables in the database according to the schema."""
    db.create_all()
    current_app.logger.info('Initialized the database.')


@click.command('reset-db')
@with_appcontext
def reset_db_command():
    """
    Drop existing database schema and create new one.
    This will delete all data!
    """
    db.drop_all()
    db.create_all()
    current_app.logger.info('Reset the database.')


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
    from flaskr.contracts.data_request import UserBotClassification
    from flaskr.processing.queries import QueryResolution, QueryWhat
    start = dt.datetime(2020, 4, 1)
    end = dt.datetime(2022, 5, 1)
    classification = UserBotClassification.BOT

    print(queries.query_users(QueryWhat.Country, classification, start, end, QueryResolution.AllTime))
    print(queries.query_users(QueryWhat.Country, classification, start, end, QueryResolution.Day))
    print(queries.query_users(QueryWhat.Country, classification, start, end, QueryResolution.Week))
    print(queries.query_users(QueryWhat.Country, classification, start, end, QueryResolution.Month))
    print(queries.query_users(QueryWhat.Country, classification, start, end, QueryResolution.Year))

    print(queries.query_views(QueryWhat.Country, classification, start, end, QueryResolution.AllTime))
    print(queries.query_views(QueryWhat.Country, classification, start, end, QueryResolution.Day))
    print(queries.query_views(QueryWhat.Country, classification, start, end, QueryResolution.Week))
    print(queries.query_views(QueryWhat.Country, classification, start, end, QueryResolution.Month))
    print(queries.query_views(QueryWhat.Country, classification, start, end, QueryResolution.Year))
