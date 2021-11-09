import os
import click
import pathlib
from flask import Flask
from flask.cli import with_appcontext
from dotenv import load_dotenv
from . import settings
from . import auth
from .database import db
from .api import traffic_api, data_api


def create_app():
    """Create and configure the Flask app."""
    # Load environment variables
    load_dotenv('.flaskenv')

    app = Flask(__name__, instance_relative_config=True)
    instance_path = pathlib.Path(app.instance_path)
    instance_path.mkdir(exist_ok=True)

    # Setup `current_app` config
    app.config.from_mapping(settings.load_from_env())
    app.config['DATABASE_PATH'] = instance_path / 'database.sqlite'
    app.config['LOG_PATH'] = instance_path / 'traffic-log.csv'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(app.config['DATABASE_PATH'].absolute())
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if not app.config['DATABASE_PATH'].exists():
        print('WARNING: No database found. Make sure to run `flask init-db`!')

    # Init flask addons
    auth.login_manager.init_app(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(traffic_api.blueprint)
    app.register_blueprint(data_api.blueprint)

    # Register click commands
    app.cli.add_command(init_db_command)
    app.cli.add_command(run_import_command)
    app.cli.add_command(process_users_command)

    return app


# TODO: MOVE TO `CLI.PY`
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Drop existing database and create new one via SQL-Alchemy."""
    db.drop_all()
    db.create_all()
    click.echo('Initialized the database.')


@click.command('run-import')
@click.argument('logfile', type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=pathlib.Path))
@with_appcontext
def run_import_command(logfile: str):
    """For temporary development usage only!"""
    traffic_api.run_import(logfile)


@click.command('process-users')
@with_appcontext
def process_users_command():
    traffic_api.process_users()
