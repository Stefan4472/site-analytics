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
from flaskr import db


class RawView(db.Model):
    """Stores raw information for a single site view."""

    __tablename__ = "raw_view"
    # Unique ID assigned to this record.
    id = db.Column(db.Integer, primary_key=True)
    # URL that received this view.
    url = db.Column(db.String, nullable=False)
    # IP address of the viewer.
    ip_address = db.Column(db.String, nullable=False)
    # User agent of the viewer.
    user_agent = db.Column(db.String, nullable=False)
    # Time at which the view was recorded.
    timestamp = db.Column(db.DateTime, nullable=False)
    # Time at which the view was processed by site-analytics.
    # Will be null if this view hasn't been processed yet.
    process_timestamp = db.Column(db.DateTime, nullable=True)
