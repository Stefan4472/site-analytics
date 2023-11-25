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
from datetime import datetime, timedelta

from flask.testing import FlaskCliRunner

from flaskr.database import db
from flaskr.models.raw_view import RawView


def test_garbage_collect_success(runner: FlaskCliRunner):
    # Note: this test is tricky because a small amount of time passes
    # between when we write to the database and when we execute the
    # command. The command calculates the GC cutoff based on the time
    # of execution. The quick hack is to base our timestamps one hour
    # in the future, but ideally we'd inject a fake clock.
    curr_time = datetime.now() + timedelta(hours=1)
    # Go back in time, adding one view per day for the last 40 days.
    for days_past in range(1, 41):
        db.session.add(
            RawView(
                url="https://www.stefanonsoftware.com",
                ip_address="123.456.7890",
                user_agent="pytest",
                timestamp=curr_time,
                process_timestamp=(curr_time - timedelta(days=days_past)),
            )
        )
        db.session.commit()
    res = runner.invoke(args=["garbage-collect", "--max_age_days=30"])
    assert res.exit_code == 0
    raw_views = RawView.query.order_by(RawView.process_timestamp).all()
    assert len(raw_views) == 30
    assert raw_views[0].process_timestamp == (curr_time - timedelta(days=30))


def test_garbage_collect_does_not_delete_unprocessed_rows(runner: FlaskCliRunner):
    for _ in range(10):
        db.session.add(
            RawView(
                url="https://www.stefanonsoftware.com",
                ip_address="123.456.7890",
                user_agent="pytest",
                timestamp=datetime.now(),
            )
        )
        db.session.commit()
    res = runner.invoke(args=["garbage-collect", "--max_age_days=30"])
    assert res.exit_code == 0
    assert len(RawView.query.all()) == 10
