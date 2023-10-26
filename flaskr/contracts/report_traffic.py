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
import marshmallow as msh
import dataclasses as dc
import datetime as dt


@dc.dataclass
class ReportTrafficContract:
    url: str
    ip_address: str
    user_agent: str
    timestamp: dt.datetime

    @staticmethod
    def get_schema() -> msh.Schema:
        return ReportTrafficSchema()

    @staticmethod
    def load(data: dict) -> 'ReportTrafficContract':
        return ReportTrafficContract.get_schema().load(data)


class ReportTrafficSchema(msh.Schema):
    url = msh.fields.Str(required=True, allow_none=False)
    ip_address = msh.fields.Str(required=True, allow_none=False)
    user_agent = msh.fields.Str(required=True, allow_none=False)
    timestamp = msh.fields.DateTime(required=True, allow_none=False)

    @msh.post_load
    def make_contract(self, data, **kwargs) -> ReportTrafficContract:
        return ReportTrafficContract(**data)
