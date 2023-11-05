"""Shared fixtures for pytest."""
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
import tempfile

import pytest

from flaskr import create_app, db
from flaskr.config import SiteConfig

# Secret key used for authenticating with the API.
PYTEST_SECRET_KEY = "dev"


@pytest.fixture
def client():
    """Creates an app with a temporary instance folder."""
    with tempfile.TemporaryDirectory() as tempdir:
        app = create_app(test_config=SiteConfig(PYTEST_SECRET_KEY, tempdir))
        with app.test_client() as client:
            with app.app_context():
                db.drop_all()
                db.create_all()
            yield client
            # Close the database connection so that we can delete the sqlite file.
            db.session.close()
            db.engine.dispose()


def make_auth_headers() -> dict:
    """Makes headers for HTTP authentication with the server."""
    return {"Authorization": PYTEST_SECRET_KEY}
