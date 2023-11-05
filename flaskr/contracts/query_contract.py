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
from typing import Optional

from marshmallow import INCLUDE, Schema, ValidationError, fields, post_load
from marshmallow_enum import EnumField

from flaskr.processing.query_runner import FilterBy, GroupBy, Query


@dataclass
class QueryContract:
    """Contract used to get a query from an incoming API request."""

    start_time: datetime
    end_time: datetime
    time_bucket: int
    group_by: Optional[GroupBy]
    filter_by: Optional[FilterBy]

    @staticmethod
    def get_schema() -> Schema:
        return QuerySchema()

    @staticmethod
    def load(data: dict) -> "QueryContract":
        return QueryContract.get_schema().load(data)

    def to_query(self) -> Query:
        return Query(
            self.start_time,
            self.end_time,
            self.time_bucket,
            self.group_by,
            self.filter_by,
        )


def validate_time_bucket(n):
    if n < 0:
        raise ValidationError("time_bucket must be greater than 0.")


class QuerySchema(Schema):
    """Marshmallow schema used to parse a `QueryContract`."""

    start_time = fields.DateTime(required=True, allow_none=False)
    end_time = fields.DateTime(required=True, allow_none=False)
    # TODO: for some reason, this doesn't actually parse the field or validate it.
    time_bucket: fields.Integer(
        required=True, allow_none=False, strict=True, validate=validate_time_bucket
    )
    group_by = EnumField(GroupBy, allow_none=True, default=None, missing=None)
    filter_by = EnumField(FilterBy, allow_none=True, default=None, missing=None)

    class Meta:
        unknown = INCLUDE

    @post_load
    def make_contract(self, data, **kwargs) -> QueryContract:
        data["time_bucket"] = int(data["time_bucket"])
        validate_time_bucket(data["time_bucket"])
        return QueryContract(**data)
