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

import marshmallow as msh
import marshmallow_enum as msh_enum

from flaskr.processing.query_runner import Filter, GroupBy, Query


@dataclass
class QueryContract:
    """Contract used to get a query from an incoming API request."""

    start_time: datetime
    end_time: datetime
    time_bucket: int
    group_by: GroupBy
    # filter_by: Filter

    @staticmethod
    def get_schema() -> msh.Schema:
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
        )


class QuerySchema(msh.Schema):
    """Marshmallow schema used to parse a `QueryContract`."""

    start_time = msh.fields.DateTime(required=True, allow_none=False)
    end_time = msh.fields.DateTime(required=True, allow_none=False)
    # time_bucket: msh.fields.Int(required=True, allow_none=False)
    group_by = msh_enum.EnumField(GroupBy, required=True, allow_none=False)

    @msh.post_load
    def make_contract(self, data, **kwargs) -> QueryContract:
        return QueryContract(**data, time_bucket=86440)
