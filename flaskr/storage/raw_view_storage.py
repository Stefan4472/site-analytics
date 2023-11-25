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
from typing import List

from flask import current_app

from flaskr import db
from flaskr.contracts.report_traffic import SinglePageView
from flaskr.models.raw_view import RawView


def write_raw_views(views: List[SinglePageView]):
    """Writes the provided view data to the database and to the backup log file."""
    with open(current_app.config["LOG_PATH"], "a", newline="") as log_file:
        writer = csv.writer(log_file, delimiter=",")
        for view in views:
            # Write to log.
            writer.writerow(
                [
                    view.timestamp.isoformat(),
                    view.url.strip(),
                    view.ip_address.strip(),
                    view.user_agent.strip(),
                ]
            )
    for view in views:
        db.session.add(
            RawView(
                url=view.url.strip(),
                ip_address=view.ip_address.strip(),
                user_agent=view.user_agent.strip(),
                timestamp=view.timestamp,
            )
        )
    db.session.commit()
