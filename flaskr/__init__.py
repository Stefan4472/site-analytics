import os
import click
import pathlib
from flask import Flask
from flask.cli import with_appcontext
from . import auth
from .database import db
from . import traffic_api
from . import data_api
from . import secret


def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__, instance_relative_config=True)

    instance_path = pathlib.Path(app.instance_path)
    instance_path.mkdir(exist_ok=True)

    # TODO: REPLACE WITH .ENV
    secret_path = os.path.join(app.instance_path, 'secret.txt')
    try:
        secret_key = secret.load_secret_key(pathlib.Path(secret_path))
    except OSError as e:
        # TODO: SET UP LOGGING
        err = 'WARNING: Couldn\'t read secret file "{}". Using default secret ' \
            'key "{}"'.format(secret_path, secret.DEFAULT_SECRET_KEY)
        raise ValueError(err)

    # Setup `current_app` config
    app.config.from_mapping(
        SECRET_KEY=secret_key,
        DATABASE_PATH=str((instance_path / 'site-traffic.sqlite').absolute()),
        LOG_PATH=str((instance_path / 'traffic-log.csv').absolute()),
        SQLALCHEMY_DATABASE_URI='sqlite:///' + str((instance_path / 'site-traffic.db').absolute()),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Init flask addons
    auth.login_manager.init_app(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(traffic_api.blueprint)
    app.register_blueprint(data_api.blueprint)
    # Register `Click` commands
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
@with_appcontext
def run_import_command():
    """For temporary development usage only!"""
    traffic_api.run_import()


@click.command('process-users')
@with_appcontext
def process_users_command():
    traffic_api.process_users()
