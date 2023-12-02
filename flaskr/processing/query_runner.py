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
from enum import Enum
from typing import Optional

import sqlalchemy as sqla
import sqlalchemy.engine

from flaskr.processing.query_result import QueryResult, calculate_num_buckets

# The maximum number of buckets allowed for query processing.
# This is configured to avoid overworking the system.
MAX_NUM_BUCKETS = 1000


class GroupBy(Enum):
    """The possible data columns that a query can aggregate on."""

    Unset = "UNSET"
    Country = "COUNTRY"
    City = "CITY"
    Region = "REGION"
    Url = "URL"
    Domain = "DOMAIN"
    OperatingSystem = "OPERATING_SYSTEM"
    Device = "DEVICE"
    DeviceType = "DEVICE_TYPE"
    Browser = "BROWSER"
    # BrowserFamily = "BROWSER_FAMILY"


class FilterBy(Enum):
    """Possible filters that can be applied to the query results."""

    Unset = "UNSET"
    Humans = "HUMANS"
    Bots = "BOTS"


@dataclass
class Query:
    """Defines a query to run over the ProcessedViews."""

    start_time: datetime
    end_time: datetime
    time_bucket: int
    group_by: Optional[GroupBy]
    filter_by: Optional[FilterBy]


def _make_select(query: Query) -> str:
    """Builds the subject of the SELECT clause of the query."""
    first_term: str
    if query.group_by is None or query.group_by == GroupBy.Unset:
        # If unset, simply select the string "Count".
        first_term = "'Count'"
    elif query.group_by == GroupBy.Country:
        first_term = "country"
    elif query.group_by == GroupBy.City:
        first_term = "city"
    elif query.group_by == GroupBy.Region:
        first_term = "region"
    elif query.group_by == GroupBy.Url:
        first_term = "url"
    elif query.group_by == GroupBy.Domain:
        first_term = "domain"
    elif query.group_by == GroupBy.OperatingSystem:
        first_term = "operating_system_family"
    elif query.group_by == GroupBy.Device:
        first_term = "device_brand"
    elif query.group_by == GroupBy.DeviceType:
        first_term = "device_type"
    elif query.group_by == GroupBy.Browser:
        first_term = "browser_family"
    else:
        raise ValueError("Not implemented")
    return f"IFNULL({first_term}, 'UNKNOWN'), timestamp"


def _make_where(query: Query) -> str:
    """Builds the content of the WHERE clause of the query."""
    sql = "timestamp >= :start_time AND timestamp <= :end_time"
    if query.filter_by == FilterBy.Bots:
        sql += " AND is_bot = TRUE"
    elif query.filter_by == FilterBy.Humans:
        sql += " AND is_bot = FALSE"
    return sql


def run_query(
    session: "sqlalchemy.orm.scoping.scoped_session", query: Query
) -> QueryResult:
    """
    Dynamically generate and execute queries over the `processed_view`
    table.

    Here's how queries work: we have a `start_time` and an `end_time`.
    The query will only process data within [start_time, end_time).

    Then we define the "time buckets" that we want to aggregate the
    data over. Time buckets are defined as a number of seconds.
    For example, setting a bucket of 3600 seconds will give you data
    aggregated for each hour between `start_time` and `end_time`.

    Then we can define an optional "group by" that we want to further
    aggregate the data over *within* the buckets. This is essentially
    choosing a column from the `processed_view` that we want to count,
    e.g. `country` or `domain`.

    Finally we can specify a filter. Only data that matches the filter
    will be processed. For example, we can specify that we only want
    to process data for bots.

    An example: "Give me the number of views per day originating
    from human users between January 1st, 2023 and January 1st, 2024,
    and furthermore break it down by country of the user."
    Can be represented as the following query:

    Query(
      start_time=datetime(2023, 1, 1),
      end_time=datetime(2024, 1, 1),
      bucket_sec=60*60*24,
      group_by=GroupBy.Country,
      filter=Filter.Humans,
    )

    TODO: how to support bucketing by calendar month? -> time_bucket could also be allowed to be a string, e.g. MONTH.
    """
    num_buckets = calculate_num_buckets(
        query.start_time, query.end_time, query.time_bucket
    )
    if num_buckets > MAX_NUM_BUCKETS:
        raise ValueError(
            f"Too many buckets: requested {num_buckets} but max is {MAX_NUM_BUCKETS}."
        )

    # Create and execute the query. We don't need to perform any GROUP BY
    # or SORT within the query, as we will handle that using our buckets.
    sql = sqla.text(
        f"SELECT {_make_select(query)} "
        "FROM processed_view "
        f"WHERE {_make_where(query)}"
    )
    raw_result = session.execute(
        sql,
        {
            "start_time": query.start_time,
            "end_time": query.end_time,
        },
    )

    # Process results and put into buckets.
    results = QueryResult(query.start_time, query.end_time, query.time_bucket)
    for r in raw_result.all():
        key = r[0]
        timestamp = datetime.fromisoformat(r[1])
        results.increment(key, timestamp)

    return results
