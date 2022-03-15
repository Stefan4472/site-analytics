import enum
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

    class Meta:
        # Define date format
        dateformat = '%m-%d-%Y'

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

    @msh.post_load
    def make_contract(self, data, **kwargs) -> DataRequestContract:
        return DataRequestContract(**data)
