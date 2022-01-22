import pathlib
from flask import Flask
from .config import SiteConfig
from . import auth
from .database import db
from .api import traffic_api, data_api
from . import cli


def create_app(test_config: SiteConfig = None):
    """Create and configure the Flask app."""
    app = Flask(__name__, instance_relative_config=True)
    instance_path = pathlib.Path(app.instance_path)
    instance_path.mkdir(exist_ok=True)

    # TODO: update unit tests
    # Set configuration. Use `test_config` if provided, otherwise load
    # from environment variables (i.e. flaskenv)
    provided_config = \
        test_config if test_config else SiteConfig.load_from_env('.flaskenv')
    app.config['SECRET_KEY'] = provided_config.secret_key
    app.config['POSTGRES_USERNAME'] = provided_config.postgres_username
    app.config['POSTGRES_PASSWORD'] = provided_config.postgres_password
    app.config['POSTGRES_HOST'] = provided_config.postgres_host
    app.config['POSTGRES_PORT'] = provided_config.postgres_port
    app.config['POSTGRES_DATABASE_NAME'] = provided_config.database_name
    app.config['LOG_PATH'] = provided_config.log_path \
        if provided_config.log_path else instance_path / 'traffic-log.csv'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = \
        bool(provided_config.sqlalchemy_track_modifications)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://'\
        f'{provided_config.postgres_username}:{provided_config.postgres_password}'\
        f'@{provided_config.postgres_host}:{provided_config.postgres_port}'\
        f'/{provided_config.database_name}'

    if app.config['SECRET_KEY'] is None:
        raise ValueError('No SECRET_KEY set')

    app.logger.info(f'DATABASE_URI: {app.config["SQLALCHEMY_DATABASE_URI"]}')
    app.logger.info(f'LOG_PATH: {app.config["LOG_PATH"]}')

    # Init flask addons
    auth.login_manager.init_app(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(traffic_api.blueprint)
    app.register_blueprint(data_api.blueprint)

    # Register click commands
    app.cli.add_command(cli.init_db_command)
    app.cli.add_command(cli.reset_db_command)
    app.cli.add_command(cli.run_import_command)
    app.cli.add_command(cli.process_data)
    app.cli.add_command(cli.debug_noodling)

    return app
