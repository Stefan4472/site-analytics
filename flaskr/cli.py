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
"""Flask CLI commands."""
from datetime import datetime, timedelta

import click
from flask import current_app
from flask.cli import with_appcontext

from flaskr.models.raw_view import RawView
from flaskr.processing.view_processor import ViewProcessor
from flaskr.storage.database import db


@click.command("reset-db")
@with_appcontext
def init_db_command():
    """
    Drops the existing database schema if it exists and create new one.
    This will delete all data!
    """
    current_app.logger.info("Initialized the database.")
    db.drop_all()
    db.create_all()
    current_app.logger.info("Reset the database.")


@click.command("process-data")
@with_appcontext
def process_data():
    current_app.logger.info("Running data processing.")
    view_processor = ViewProcessor()
    num_processed = 0
    for raw_view in RawView.query.filter_by(process_timestamp=None):
        current_app.logger.debug(f"Processing id={raw_view.id}.")
        processed = view_processor.process_view(raw_view)
        raw_view.process_timestamp = processed.process_timestamp
        db.session.add(processed)
        num_processed += 1
        if (num_processed % 500) == 0:
            current_app.logger.info(
                f"Committing after processing {num_processed} views."
            )
            db.session.commit()
    db.session.commit()
    click.echo(f"Processed {num_processed} records.")


@click.command("garbage-collect")
@click.option(
    "--max_age_days",
    type=int,
    default=30,
    help="The maximum age of data (in days) to keep.",
)
@with_appcontext
def garbage_collect(max_age_days: int):
    """
    Deletes raw_views older than `max_age_days`.

    We don't need to be too careful because all views are also written to a log file.
    """
    current_app.logger.info("Running garbage collection.")
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    current_app.logger.info(f"Cutoff date is {cutoff_date}")
    num_deleted = (
        RawView.query.filter(RawView.process_timestamp is not None)
        .filter(RawView.process_timestamp < cutoff_date)
        .delete()
    )
    current_app.logger.info(f"Deleted {num_deleted} rows.")
