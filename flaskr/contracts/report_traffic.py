import marshmallow as msh
import dataclasses as dc


@dc.dataclass
class ReportTrafficContract:
    url: str
    ip_address: str
    user_agent: str

    @staticmethod
    def get_schema() -> msh.Schema:
        return ReportTrafficSchema()


class ReportTrafficSchema(msh.Schema):
    url = msh.fields.Str(required=True, allow_none=False)
    ip_address = msh.fields.Str(required=True, allow_none=False)
    user_agent = msh.fields.Str(required=True, allow_none=False)

    @msh.post_load
    def make_contract(self, data, **kwargs) -> ReportTrafficContract:
        return ReportTrafficContract(**data)
