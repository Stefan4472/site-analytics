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
import csv
from datetime import datetime

from flask import Flask

from flaskr.models.raw_view import RawView
from flaskr.storage.raw_view_storage import write_raw_views


def test_storage_success(app: Flask):
    views = [
        RawView(
            url=f"https://www.stefanonsoftware.com/{i}",
            ip_address=f"123.456.7890-{i}",
            user_agent=f"pytest-{i}",
            timestamp=datetime.now(),
        )
        for i in range(10)
    ]
    write_raw_views(views)
    stored_views = RawView.query.order_by(RawView.timestamp).all()
    assert len(stored_views) == 10
    for i, stored_view in enumerate(stored_views):
        assert stored_view.url == views[i].url
        assert stored_view.ip_address == views[i].ip_address
        assert stored_view.user_agent == views[i].user_agent
        assert stored_view.timestamp == views[i].timestamp


def test_storage_writes_log_file(app: Flask):
    views = [
        RawView(
            url=f"https://www.stefanonsoftware.com/{i}",
            ip_address=f"123.456.7890-{i}",
            user_agent=f"pytest-{i}",
            timestamp=datetime.now(),
        )
        for i in range(10)
    ]
    write_raw_views(views)
    with open(app.config["LOG_PATH"], newline="") as log_file:
        reader = csv.reader(log_file)
        for i, row in enumerate(reader):
            assert row[0] == views[i].timestamp.isoformat()
            assert row[1] == views[i].url
            assert row[2] == views[i].ip_address
            assert row[3] == views[i].user_agent
