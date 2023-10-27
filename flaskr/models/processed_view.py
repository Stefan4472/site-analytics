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


class ProcessedView(db.Model):
    """
    Stores raw information for a single site view that has been processed by
    site-analytics.
    """

    __tablename__ = "processed_view"
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

    # Whether the requester was classified as being a bot.
    is_bot = db.Column(db.Boolean)
    # Hostname of the IP address used by the requestor.
    # Only populated if `is_bot=True`.
    hostname = db.Column(db.String, nullable=True)
    # Domain of the requestor's hostname.
    # Only populated if `is_bot=True`.
    domain = db.Column(db.String, nullable=True)

    # Location information derived from the IP address of the requstor.
    # Fields may be null if they could not be determined.
    country = db.Column(db.String, nullable=True)
    region = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=True)
    zip = db.Column(db.String, nullable=True)
    lat = db.Column(db.String, nullable=True)
    lon = db.Column(db.String, nullable=True)
    isp = db.Column(db.String, nullable=True)
    org = db.Column(db.String, nullable=True)

    # Device information derived from the user agent of the requestor.
    # Fields may be null if they could not be determined.
    operating_system_family = db.Column(db.String, nullable=True)
    operating_system_version = db.Column(db.String, nullable=True)
    browser_family = db.Column(db.String, nullable=True)
    browser_version = db.Column(db.String, nullable=True)
    device_family = db.Column(db.String, nullable=True)
    device_brand = db.Column(db.String, nullable=True)
    device_type = db.Column(db.String, nullable=True)
