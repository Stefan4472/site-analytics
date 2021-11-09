import pathlib
from flask import Flask
from dotenv import load_dotenv
from . import settings
from . import auth
from .database import db
from .api import traffic_api, data_api
from . import cli


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

    app.logger.info('DATABASE_PATH: {}'.format(app.config['DATABASE_PATH']))
    app.logger.info('LOG_PATH: {}'.format(app.config['LOG_PATH']))
    app.logger.info('SECRET_KEY: {}'.format(app.config['SECRET_KEY']))

    if not app.config['DATABASE_PATH'].exists():
        app.logger.warning('WARNING: No database found. Make sure to run `flask init-db`!')

    # Init flask addons
    auth.login_manager.init_app(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(traffic_api.blueprint)
    app.register_blueprint(data_api.blueprint)

    # Register click commands
    app.cli.add_command(cli.init_db_command)
    app.cli.add_command(cli.run_import_command)
    app.cli.add_command(cli.process_data)
    app.cli.add_command(cli.debug_noodling)

    return app
