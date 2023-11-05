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
from datetime import datetime

from flask.testing import FlaskClient

from flaskr.models.raw_view import RawView
from flaskr.test.conftest import make_auth_headers


def test_report_traffic(client: FlaskClient):
    curr_time = datetime.now()
    res = client.post(
        "/api/v1/traffic",
        json={
            "url": "https://www.stefanonsoftware.com",
            "ip_address": "123.456.7890",
            "user_agent": "Pytest",
            "timestamp": curr_time.isoformat(),
        },
        headers=make_auth_headers(),
    )
    assert res.status == "200 OK"

    raw_views = RawView.query.all()
    assert len(raw_views) == 1
    assert raw_views[0].url == r"https://www.stefanonsoftware.com"
    assert raw_views[0].ip_address == "123.456.7890"
    assert raw_views[0].user_agent == "Pytest"
    assert raw_views[0].timestamp == curr_time
