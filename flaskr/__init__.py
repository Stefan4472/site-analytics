# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os

from flask import Flask

from .config import SiteConfig, validate_config
from .database import db


def create_app(test_config: SiteConfig = None):
    """Creates the Flask app. Uses the provided `test_config`, if non-Null."""
    app = Flask(__name__, instance_relative_config=True)

    # Load config from environment variables, unless a test config has been passed in.
    site_config = test_config if test_config else SiteConfig.load_from_env()
    validate_config(site_config)

    app.instance_path = site_config.instance_path
    os.makedirs(app.instance_path, exist_ok=True)

    app.config["SECRET_KEY"] = site_config.secret_key
    # File where all received data is written out in CSV format as a backup.
    app.config["LOG_PATH"] = os.path.join(app.instance_path, "log.csv")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        app.instance_path, "db.sqlite"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.logger.info(f'LOG_PATH: {app.config["LOG_PATH"]}')
    app.logger.info(f'DATABASE_URI: {app.config["SQLALCHEMY_DATABASE_URI"]}')

    # Initialize flask addons.
    from . import auth, cli

    auth.login_manager.init_app(app)
    db.init_app(app)

    # Register blueprints.
    from .api import data_api, traffic_api

    app.register_blueprint(traffic_api.blueprint)
    app.register_blueprint(data_api.blueprint)

    # Register click commands.
    app.cli.add_command(cli.init_db_command)
    app.cli.add_command(cli.reset_db_command)
    app.cli.add_command(cli.process_data)
    app.cli.add_command(cli.garbage_collect)

    return app
