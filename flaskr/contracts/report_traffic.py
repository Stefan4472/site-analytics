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
