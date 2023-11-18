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

from flaskr.api.traffic_api import MAX_ALLOWED_VIEWS_PER_REQUEST
from flaskr.models.raw_view import RawView
from flaskr.test.conftest import make_auth_headers


def test_report_traffic_success(client: FlaskClient):
    curr_time = datetime.now()
    res = client.post(
        "/api/v1/traffic",
        json={
            "traffic": [
                {
                    "url": "https://www.stefanonsoftware.com/test-1",
                    "ip_address": "123.456.7890",
                    "user_agent": "Pytest",
                    "timestamp": curr_time.isoformat(),
                },
                {
                    "url": "https://www.stefanonsoftware.com/test-2",
                    "ip_address": "234.567.8901",
                    "user_agent": "Pytest",
                    "timestamp": curr_time.isoformat(),
                },
                {
                    "url": "https://www.stefanonsoftware.com/test-3",
                    "ip_address": "345.678.9012",
                    "user_agent": "Pytest",
                    "timestamp": curr_time.isoformat(),
                },
            ]
        },
        headers=make_auth_headers(),
    )
    assert res.status == "200 OK"

    raw_views = RawView.query.order_by(RawView.ip_address).all()
    assert len(raw_views) == 3
    assert raw_views[0].url == r"https://www.stefanonsoftware.com/test-1"
    assert raw_views[0].ip_address == "123.456.7890"
    assert raw_views[0].user_agent == "Pytest"
    assert raw_views[0].timestamp == curr_time

    assert raw_views[1].url == r"https://www.stefanonsoftware.com/test-2"
    assert raw_views[1].ip_address == "234.567.8901"
    assert raw_views[1].user_agent == "Pytest"
    assert raw_views[1].timestamp == curr_time

    assert raw_views[2].url == r"https://www.stefanonsoftware.com/test-3"
    assert raw_views[2].ip_address == "345.678.9012"
    assert raw_views[2].user_agent == "Pytest"
    assert raw_views[2].timestamp == curr_time


def test_report_traffic_fails_when_empty(client: FlaskClient):
    res = client.post(
        "/api/v1/traffic",
        json={"traffic": []},
        headers=make_auth_headers(),
    )
    assert res.text == "The request did not contain any traffic records."
    assert res.status == "400 BAD REQUEST"


def test_report_traffic_fails_when_too_large(client: FlaskClient):
    curr_time = datetime.now()
    res = client.post(
        "/api/v1/traffic",
        json={
            "traffic": (MAX_ALLOWED_VIEWS_PER_REQUEST + 1)
            * [
                {
                    "url": "https://www.stefanonsoftware.com/test-1",
                    "ip_address": "123.456.7890",
                    "user_agent": "Pytest",
                    "timestamp": curr_time.isoformat(),
                }
            ]
        },
        headers=make_auth_headers(),
    )
    assert "Too many traffic records" in res.text
    assert res.status == "400 BAD REQUEST"


def test_report_traffic_fails_when_unauthorized(client: FlaskClient):
    res = client.post(
        "/api/v1/traffic",
        json={
            "traffic": [
                {
                    "url": "https://www.stefanonsoftware.com/test-1",
                    "ip_address": "123.456.7890",
                    "user_agent": "Pytest",
                    "timestamp": datetime.now().isoformat(),
                }
            ]
        },
        headers={},
    )
    assert res.status == "401 UNAUTHORIZED"
