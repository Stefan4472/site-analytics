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
import pathlib
import time

import click
from flask import current_app
from flask.cli import with_appcontext

import flaskr.api.traffic_api as traffic_api
from flaskr.contracts.report_traffic import ReportTrafficContract
from flaskr.database import db
from flaskr.models.raw_view import RawView
from flaskr.processing.view_processor import ViewProcessor

"""Flask CLI commands."""


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Create tables in the database according to the schema."""
    db.create_all()
    current_app.logger.info("Initialized the database.")


@click.command("reset-db")
@with_appcontext
def reset_db_command():
    """
    Drop existing database schema and create new one.
    This will delete all data!
    """
    db.drop_all()
    db.create_all()
    current_app.logger.info("Reset the database.")


@click.command("process-data")
@with_appcontext
def process_data():
    current_app.logger.info("Running data processing")
    view_processor = ViewProcessor()
    num_processed = 0
    for raw_view in RawView.query.filter_by(process_timestamp=None):
        current_app.logger.debug(f"Processing id={raw_view.id}.")
        processed = view_processor.process_view(raw_view)
        raw_view.process_timestamp = processed.process_timestamp
        db.session.add(processed)
        num_processed += 1
    db.session.commit()
    click.echo(f"Processed {num_processed} records.")
