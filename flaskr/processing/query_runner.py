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
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import List

import sqlalchemy as sqla
import sqlalchemy.engine

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
    BrowserFamily = "BROWSER_FAMILY"


class Filter(Enum):
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
    # group_by: GroupBy TODO
    # filter: Filter TODO


# TODO: pretty sure this copies the data when serializing to JSON.
# Would be good to just "natively" have it in the JSON dict.
@dataclass
class Bucket:
    """Stores query results from a single "bucket" of time."""

    # Timestamp at which the bucket starts.
    timestamp: datetime
    # Data stored for this bucket, keyed by the "group_by" of the query.
    data: defaultdict[str, int] = field(default_factory=lambda: defaultdict(int))

    def json(self) -> dict:
        """Serialize this bucket to a JSON object."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }


# def build_filter(self, start_time, end_time, filter_):
#     # Build the WHERE clause
#     return ''
#
# def get_column_name(self) -> Optional[str]:
#     if self == GroupWhat.Nothing:
#         return None
#     elif self == GroupWhat.Country:
#         return "users.country"
#     elif self == GroupWhat.City:
#         return "users.city"
#     elif self == GroupWhat.Region:
#         return "users.region"
#     elif self == GroupWhat.Url:
#         return "views.url"
#     elif self == GroupWhat.Domain:
#         return "users.domain"
#     elif self == GroupWhat.OperatingSystem:
#         return "views.operating_system"
#     elif self == GroupWhat.Device:
#         return "views.device"
#     elif self == GroupWhat.DeviceType:
#         return "views.device_type"
#     elif self == GroupWhat.Browser:
#         return "views.browser"
#     else:
#         raise ValueError("Not implemented")


def run_query(
    session: "sqlalchemy.orm.scoping.scoped_session", query: Query
) -> List[Bucket]:
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
    num_buckets = int(
        (query.end_time - query.start_time).total_seconds() / query.time_bucket
    )
    if num_buckets > MAX_NUM_BUCKETS:
        raise ValueError(
            f"Too many buckets: the limit is {MAX_NUM_BUCKETS} but the query requested {num_buckets}. query={query}"
        )

    # Initialize the buckets.
    buckets = []
    curr_time = query.start_time
    for _ in range(num_buckets):
        buckets.append(Bucket(curr_time))
        curr_time += timedelta(seconds=query.time_bucket)

    # TODO: SELECT clause and filter
    # Create and execute the query. We don't need to perform any GROUP BY
    # or SORT within the query, as we will handle that using our buckets.
    sql = sqla.text(
        "SELECT timestamp "
        "FROM processed_view "
        "WHERE timestamp >= :start_time AND timestamp <= :end_time"
    )
    params = {
        "start_time": query.start_time,
        "end_time": query.end_time,
    }
    result = session.execute(sql, params)

    # Put data into buckets.
    for r in result.all():
        timestamp = datetime.fromisoformat(r[0])
        bucket_index = int(
            (timestamp - query.start_time).total_seconds() / query.time_bucket
        )
        buckets[bucket_index].data["count"] += 1

    return buckets
