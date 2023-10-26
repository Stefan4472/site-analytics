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
import dataclasses as dc
import datetime as dt
from enum import Enum
from typing import List, Optional

import sqlalchemy as sqla
import sqlalchemy.engine

import flaskr.processing.util as util


class QueryOn(Enum):
    People = "People"
    Bots = "Bots"


class CountWhat(Enum):
    Views = "Views"
    Users = "Users"


class GroupWhat(Enum):
    Nothing = "Nothing"
    Country = "Country"
    City = "City"
    Region = "Region"
    Url = "Url"
    Domain = "Domain"
    OperatingSystem = "OperatingSystem"
    Device = "Device"
    DeviceType = "DeviceType"
    Browser = "Browser"

    def get_column_name(self) -> Optional[str]:
        if self == GroupWhat.Nothing:
            return None
        elif self == GroupWhat.Country:
            return "users.country"
        elif self == GroupWhat.City:
            return "users.city"
        elif self == GroupWhat.Region:
            return "users.region"
        elif self == GroupWhat.Url:
            return "views.url"
        elif self == GroupWhat.Domain:
            return "users.domain"
        elif self == GroupWhat.OperatingSystem:
            return "views.operating_system"
        elif self == GroupWhat.Device:
            return "views.device"
        elif self == GroupWhat.DeviceType:
            return "views.device_type"
        elif self == GroupWhat.Browser:
            return "views.browser"
        else:
            raise ValueError("Not implemented")


class QueryResolution(Enum):
    All = "All"  # No resolution into Days/Weeks/Months etc.
    Day = "Day"
    Week = "Week"
    Month = "Month"
    Year = "Year"


@dc.dataclass
class Query:
    query_on: QueryOn
    count_what: CountWhat
    group_what: GroupWhat
    resolution: QueryResolution
    # Dates default to MIN and MAX, giving you the ALL TIME results
    start_date: dt.date = None
    end_date: dt.date = None


@dc.dataclass
class QueryResult:
    quantity: int
    date: dt.datetime = None
    key: str = None


class QueryRunner:
    """
    Dynamically generate and execute queries.

    This is pretty complicated, but it's the only feasible way to cover
    all TimePeriod * Selection combinations. I don't know if this will
    be the way-to-go long term, because it makes schema changes tough.

    See `test_query_runner.py` for examples of queries and generated SQL.
    """

    @staticmethod
    def run_query(
        query: Query,
        session: "sqlalchemy.orm.scoping.scoped_session",
    ) -> List[QueryResult]:
        sql = sqla.text(QueryRunner._generate_sql(query))
        params = {
            "is_bot": query.query_on == QueryOn.Bots,
            "start": query.start_date if query.start_date else dt.date.min,
            "end": query.end_date if query.end_date else dt.date.max,
        }
        result = session.execute(sql, params)
        return QueryRunner._make_results(query, result)

    @staticmethod
    def _generate_sql(query: Query) -> str:
        """
        Dynamically generate SQL for the given query.

        This is a little hairy. I've done my best to make it readable.
        There are still some logic simplifications that could be done in the
        GROUP BY section.
        """
        if query.count_what == CountWhat.Users:
            query_string = "SELECT COUNT(DISTINCT users.id) AS cnt"
        else:
            query_string = "SELECT COUNT(*) AS cnt"

        # Select specified "QueryWhat" column
        if query.group_what != GroupWhat.Nothing:
            query_string += ", " + query.group_what.get_column_name()

        # Select date values for "QueryResolution" (if resolution != AllTime)
        if query.resolution == QueryResolution.Day:
            query_string += ", EXTRACT(YEAR FROM views.timestamp) AS year, EXTRACT(DOY FROM views.timestamp) AS day"
        elif query.resolution == QueryResolution.Week:
            # Note: here we need to extract ISOYEAR, not YEAR, because the WEEK
            # crosses over YEAR boundaries, e.g. the last week of December.
            # Using YEAR alone causes a bug where the year and week don't match up.
            query_string += ", EXTRACT(ISOYEAR FROM views.timestamp) AS year, EXTRACT(WEEK FROM views.timestamp) AS week"
        elif query.resolution == QueryResolution.Month:
            query_string += ", EXTRACT(YEAR FROM views.timestamp) AS year, EXTRACT(MONTH FROM views.timestamp) AS month"
        elif query.resolution == QueryResolution.Year:
            query_string += ", EXTRACT(YEAR FROM views.timestamp) AS year"

        query_string += (
            " FROM users JOIN views ON views.user_id = users.id "
            "WHERE views.timestamp > :start AND views.timestamp < :end "
            "AND users.is_bot = :is_bot"
        )

        # Assemble GROUP BY (unless resolution == AllTime and QueryWhat == Nothing)
        if not (
            query.resolution == QueryResolution.All
            and query.group_what == GroupWhat.Nothing
        ):
            query_string += " GROUP BY "
            if query.resolution == QueryResolution.All:
                # No dates involved: just GROUP BY the selected column
                query_string += query.group_what.get_column_name()
            else:
                # GROUP BY date first
                if query.resolution == QueryResolution.Day:
                    query_string += "year, day"
                elif query.resolution == QueryResolution.Week:
                    query_string += "year, week"
                elif query.resolution == QueryResolution.Month:
                    query_string += "year, month"
                elif query.resolution == QueryResolution.Year:
                    query_string += "year"
                # Then GROUP BY selected column
                if query.group_what != GroupWhat.Nothing:
                    query_string += ", " + query.group_what.get_column_name()

        query_string += " ORDER BY "
        # ORDER BY date if resolution != AllTime
        if query.resolution == QueryResolution.Day:
            query_string += "year, day, "
        elif query.resolution == QueryResolution.Week:
            query_string += "year, week, "
        elif query.resolution == QueryResolution.Month:
            query_string += "year, month, "
        elif query.resolution == QueryResolution.Year:
            query_string += "year, "
        # Then order by "QueryWhat" column
        if query.group_what == GroupWhat.Nothing:
            query_string += "cnt"
        else:
            query_string += query.group_what.get_column_name()

        return query_string

    @staticmethod
    def _make_results(
        query: Query,
        result: sqlalchemy.engine.CursorResult,
    ) -> List[QueryResult]:
        """
        Given an SQLAlchemy Cursor that resulted from executing the query,
        return a list of QueryResults.
        """
        has_key = query.group_what != GroupWhat.Nothing
        # The index at which date information starts depends on whether
        # we queried on something besides the total count.
        date_index = 2 if has_key else 1

        if query.resolution == QueryResolution.All:
            return [
                QueryResult(r[0], key=r[1] if has_key else None) for r in result.all()
            ]
        elif query.resolution == QueryResolution.Day:
            return [
                QueryResult(
                    r[0],
                    key=r[1] if has_key else None,
                    date=util.datetime_from_day(r[date_index], r[date_index + 1]),
                )
                for r in result.all()
            ]
        elif query.resolution == QueryResolution.Week:
            return [
                QueryResult(
                    r[0],
                    key=r[1] if has_key else None,
                    date=util.datetime_from_week(r[date_index], r[date_index + 1]),
                )
                for r in result.all()
            ]
        elif query.resolution == QueryResolution.Month:
            return [
                QueryResult(
                    r[0],
                    key=r[1] if has_key else None,
                    date=util.datetime_from_month(r[date_index], r[date_index + 1]),
                )
                for r in result.all()
            ]
        elif query.resolution == QueryResolution.Year:
            return [
                QueryResult(
                    r[0],
                    key=r[1] if has_key else None,
                    date=util.datetime_from_year(r[date_index]),
                )
                for r in result.all()
            ]
