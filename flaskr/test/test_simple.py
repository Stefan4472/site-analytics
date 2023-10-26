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
import tempfile
import pytest
import pathlib
from flaskr import create_app
from flaskr import db
from flaskr.config import SiteConfig


# TODO: SET UP A .FLASKENV FOR TESTING
PYTEST_SECRET_KEY = 'dev'
PYTEST_POSTGRES_USERNAME = '<INSERT_TESTER_USERNAME>'
PYTEST_POSTGRES_PASSWORD = '<INSERT_TESTER_PASSWORD>'
PYTEST_POSTGRES_HOST = '127.0.0.1'
PYTEST_POSTGRES_PORT = 5433
PYTEST_POSTGRES_DATABASE_NAME = 'test_siteanalytics'


@pytest.fixture
def client():
    # Create temporary file for logging
    log_fd, log_path = tempfile.mkstemp()

    app = create_app(SiteConfig(
        PYTEST_SECRET_KEY,
        PYTEST_POSTGRES_USERNAME,
        PYTEST_POSTGRES_PASSWORD,
        PYTEST_POSTGRES_HOST,
        PYTEST_POSTGRES_PORT,
        PYTEST_POSTGRES_DATABASE_NAME,
        log_path=pathlib.Path(log_path),
    ))

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client

    os.close(log_fd)
    os.unlink(log_path)


def test_traffic(client):
    """Start with a blank database."""
    res = client.post('/api/v1/traffic', json={
        'url': '/',
        'ip_address': '1234',
        'user_agent': 'Pytest',
    }, headers={'Authorization': PYTEST_SECRET_KEY})
    assert res.status == '200 OK'


def test_users(client):
    res = client.get('/api/v1/data/statistics', query_string={
        'query_on': 'Bots',
        'count_what': 'Views',
        'group_what': 'Country',
        'resolution': 'Week',
        'start_date': '2020-4-1',
        'end_date': '2022-5-1',
    }, headers={'Authorization': PYTEST_SECRET_KEY})
    assert res.status == '200 OK'
    assert res.data == b'[]\n'
