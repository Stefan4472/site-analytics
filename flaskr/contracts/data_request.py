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
import datetime as dt
import marshmallow as msh
import dataclasses as dc
import marshmallow_enum as msh_enum
from flaskr.processing.query_runner import Query, QueryOn, CountWhat, QueryResolution, GroupWhat


@dc.dataclass
class DataRequestContract:
    """General-purpose contract for retrieving data from the API."""
    query_on: QueryOn
    count_what: CountWhat
    group_what: GroupWhat
    resolution: QueryResolution
    start_date: dt.date = None
    end_date: dt.date = None

    @staticmethod
    def get_schema() -> msh.Schema:
        return DataRequestSchema()

    @staticmethod
    def load(data: dict) -> 'DataRequestContract':
        return DataRequestContract.get_schema().load(data)

    def to_query(self) -> Query:
        return Query(
            self.query_on, self.count_what, self.group_what,
            self.resolution, self.start_date, self.end_date
        )


class DataRequestSchema(msh.Schema):
    # TODO: need to parse dates as UTC-timezones, because Psycopg automatically interprets as UTC
    query_on = msh_enum.EnumField(QueryOn, required=True, allow_none=False)
    count_what = msh_enum.EnumField(CountWhat, required=True, allow_none=False)
    group_what = msh_enum.EnumField(GroupWhat, required=True, allow_none=False)
    resolution = msh_enum.EnumField(QueryResolution, required=True, allow_none=False)
    start_date = msh.fields.Date(required=False, allow_none=True)
    end_date = msh.fields.Date(required=False, allow_none=True)

    class Meta:
        # Define date format
        dateformat = '%m-%d-%Y'

    @msh.post_load
    def make_contract(self, data, **kwargs) -> DataRequestContract:
        return DataRequestContract(**data)
