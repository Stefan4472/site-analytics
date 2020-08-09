import os
import click
from flask import Flask, current_app, g
from flask.cli import with_appcontext
from . import database_context
from . import backend


def create_app():
    """Create and configure the app.

    Starter code from https://flask.palletsprojects.com/en/1.1.x/tutorial/
    """
    app = Flask(__name__, instance_relative_config=True)
    # Setup `current_app` config
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE_PATH=os.path.join(app.instance_path, 'site-traffic.sqlite'),
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
    # Register "backend" Blueprint
    app.register_blueprint(backend.blueprint)
    # Register `close_db()` on app teardown
    app.teardown_appcontext(database_context.close_db)
    # Register `Click` commands
    app.cli.add_command(init_db_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Re-initialize the database with the schema."""
    database_context.init_db()
    click.echo('Initialized the database.')