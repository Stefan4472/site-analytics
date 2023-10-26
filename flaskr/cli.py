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
from datetime import datetime

import click
from flask import current_app
from flask.cli import with_appcontext

import flaskr.api.traffic_api as traffic_api
from flaskr.contracts.report_traffic import ReportTrafficContract
from flaskr.database import db
from flaskr.models.user import User

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


@click.command("run-import")
@click.argument(
    "logfile",
    type=click.Path(
        exists=True, dir_okay=False, file_okay=True, path_type=pathlib.Path
    ),
)
@with_appcontext
def run_import_command(logfile: pathlib.Path):
    """For temporary development usage only!"""
    current_app.logger.info(f"Running import on logfile {logfile.absolute()}")
    with open(logfile) as f:
        for line in f:
            first_comma = line.index(",")
            second_comma = line.index(",", first_comma + 1)
            third_comma = line.index(",", second_comma + 1)

            timestamp = line[:first_comma]
            request_time = datetime.strptime(timestamp, "%m-%d-%Y-%H:%M:%S:%f")
            url = line[first_comma + 1 : second_comma]
            ip = line[second_comma + 1 : third_comma]
            user_agent = line[third_comma + 1 :]

            contract = ReportTrafficContract(url, ip, user_agent, request_time)
            traffic_api.store_traffic(contract)


@click.command("process-data")
@with_appcontext
def process_data():
    current_app.logger.info("Running data processing")
    for user in User.query.filter_by(was_processed=False):
        try:
            current_app.logger.info(f"Processing User {user.id}")
            user.process()
            db.session.commit()  # TODO: move this out of the loop once we're sure it doesn't fail
        except ValueError as e:
            current_app.logger.error(f"Failure processing user {user.id}: {e}")
        # Sleep to avoid exceeding the Geo-IP API rate limit
        time.sleep(1)


# TODO: remove
@click.command("debug-noodling")
@with_appcontext
def debug_noodling():
    import datetime as dt

    from flaskr.processing.query_runner import (CountWhat, GroupWhat, Query,
                                                QueryOn, QueryResolution,
                                                QueryResult, QueryRunner)

    start = dt.datetime(2020, 4, 1)
    end = dt.datetime(2022, 5, 1)

    print(
        QueryRunner.run_query(
            Query(
                QueryOn.Bots,
                CountWhat.Users,
                GroupWhat.Country,
                QueryResolution.All,
                start,
                end,
            ),
            db.session,
        )
    )
    print(
        QueryRunner.run_query(
            Query(
                QueryOn.Bots,
                CountWhat.Users,
                GroupWhat.Country,
                QueryResolution.Day,
                start,
                end,
            ),
            db.session,
        )
    )
    print(
        QueryRunner.run_query(
            Query(
                QueryOn.Bots,
                CountWhat.Users,
                GroupWhat.Country,
                QueryResolution.Week,
                start,
                end,
            ),
            db.session,
        )
    )
    print(
        QueryRunner.run_query(
            Query(
                QueryOn.Bots,
                CountWhat.Users,
                GroupWhat.Country,
                QueryResolution.Month,
                start,
                end,
            ),
            db.session,
        )
    )
    print(
        QueryRunner.run_query(
            Query(
                QueryOn.Bots,
                CountWhat.Users,
                GroupWhat.Country,
                QueryResolution.Year,
                start,
                end,
            ),
            db.session,
        )
    )

    print(
        QueryRunner.run_query(
            Query(
                QueryOn.Bots,
                CountWhat.Views,
                GroupWhat.Country,
                QueryResolution.Day,
                start,
                end,
            ),
            db.session,
        )
    )
    print(
        QueryRunner.run_query(
            Query(
                QueryOn.Bots,
                CountWhat.Views,
                GroupWhat.Country,
                QueryResolution.Week,
                start,
                end,
            ),
            db.session,
        )
    )
    print(
        QueryRunner.run_query(
            Query(
                QueryOn.Bots,
                CountWhat.Views,
                GroupWhat.Country,
                QueryResolution.Month,
                start,
                end,
            ),
            db.session,
        )
    )
    print(
        QueryRunner.run_query(
            Query(
                QueryOn.Bots,
                CountWhat.Views,
                GroupWhat.Country,
                QueryResolution.Year,
                start,
                end,
            ),
            db.session,
        )
    )
    print(
        QueryRunner.run_query(
            Query(
                QueryOn.Bots,
                CountWhat.Views,
                GroupWhat.Country,
                QueryResolution.All,
                start,
                end,
            ),
            db.session,
        )
    )
