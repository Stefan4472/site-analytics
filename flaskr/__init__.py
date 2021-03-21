import os
import click
import pathlib
from flask import Flask
from flask.cli import with_appcontext
from . import auth
from . import database_context
from . import traffic_api
from . import data_api
from . import secret


def create_app():
    """Create and configure the app.

    Starter code from https://flask.palletsprojects.com/en/1.1.x/tutorial/
    """
    app = Flask(__name__, instance_relative_config=True)
    auth.login_manager.init_app(app)

    secret_path = os.path.join(app.instance_path, 'secret.txt')
    try:
        secret_key = secret.load_secret_key(pathlib.Path(secret_path))
    except OSError as e:
        print(
            'WARNING: Couldn\'t read secret file "{}". Using default secret ' \
                'key "{}"'.format(secret_path, secret.DEFAULT_SECRET_KEY)
        )
        secret_key = secret.DEFAULT_SECRET_KEY

    # Setup `current_app` config
    # TODO: BETTER WAY TO CACHE `ACTIVE_SESSIONS`?
    app.config.from_mapping(
        SECRET_KEY=secret_key,
        DATABASE_PATH=os.path.join(app.instance_path, 'site-traffic.sqlite'),
        LOG_PATH=os.path.join(app.instance_path, 'traffic-log.csv'),
    )

    # Load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)

    # Ensure that the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    init_app(app)
    return app


def init_app(app):
    """Initialize the provided application context."""
    # Register blueprints
    app.register_blueprint(traffic_api.blueprint)
    app.register_blueprint(data_api.blueprint)
    # Register `close_db()` on app teardown (end-of-request)
    app.teardown_appcontext(database_context.close_db)
    # Register `Click` commands
    # app.cli.add_command(init_db_command)
    app.cli.add_command(process_cached_sessions_command)
    app.cli.add_command(cleanup_cached_sessions_command)


# TODO: THIS NO LONGER WORKS BECAUSE THE SCHEMA HAS BEEN MOVED TO A DIFFERENT FOLDER
# @click.command('init-db')
# @with_appcontext
# def init_db_command():
#     """Re-initialize the database with the schema."""
#     database_context.init_db()
#     click.echo('Initialized the database.')


@click.command('process-cached-sessions')
@with_appcontext
def process_cached_sessions_command():
    traffic_api.process_cached_sessions()


@click.command('cleanup-cached-sessions')
@with_appcontext
def cleanup_cached_sessions_command():
    rows_deleted = \
        database_context.get_db().cleanup_cached_sessions(commit=True)
    click.echo('Deleted {} stale records'.format(rows_deleted))

