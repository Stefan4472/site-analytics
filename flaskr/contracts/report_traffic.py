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
from dataclasses import dataclass
from datetime import datetime
from typing import List

from marshmallow import (Schema, ValidationError, fields, post_load,
                         validates_schema)


@dataclass
class SinglePageView:
    """A single reported page view."""

    url: str
    ip_address: str
    user_agent: str
    timestamp: datetime


@dataclass
class ReportTrafficContract:
    """Some number of page views reported to the API."""

    views: List[SinglePageView]

    @staticmethod
    def get_schema() -> Schema:
        return ReportTrafficSchema()

    @staticmethod
    def load(data: dict) -> "ReportTrafficContract":
        return ReportTrafficContract.get_schema().load(data)


class SinglePageViewSchema(Schema):
    """The schema for SinglePageView."""

    url = fields.Str(required=True, allow_none=False)
    ip_address = fields.Str(required=True, allow_none=False)
    user_agent = fields.Str(required=True, allow_none=False)
    timestamp = fields.DateTime(required=True, format="iso", allow_none=False)


class ReportTrafficSchema(Schema):
    """The schema for ReportTrafficContract."""

    traffic = fields.List(fields.Nested(SinglePageViewSchema))

    @post_load
    def make_contract(self, data, **kwargs) -> ReportTrafficContract:
        return ReportTrafficContract([SinglePageView(**d) for d in data["traffic"]])
