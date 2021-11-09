import enum
import datetime as dt
import marshmallow as msh
import dataclasses as dc
import marshmallow_enum as msh_enum


class UserBotClassification(enum.Enum):
    """Used to distinguish whether a query is on Users or Bots."""
    BOT = 'BOT'
    USER = 'USER'

    def is_bot(self) -> bool:
        return self == UserBotClassification.BOT


@dc.dataclass
class DataRequestContract:
    """General-purpose contract for retrieving data from the API."""
    start_date: dt.date
    end_date: dt.date
    classification: UserBotClassification

    class Meta:
        # Define date format
        dateformat = '%m-%d-%Y'

    @staticmethod
    def get_schema() -> msh.Schema:
        return DataRequestSchema()


class DataRequestSchema(msh.Schema):
    start_date = msh.fields.Date(required=True, allow_none=False)
    end_date = msh.fields.Date(required=True, allow_none=False)
    classification = msh_enum.EnumField(UserBotClassification, required=True, allow_none=False)

    @msh.post_load
    def make_contract(self, data, **kwargs) -> DataRequestContract:
        return DataRequestContract(**data)
