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
import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Set


def calculate_num_buckets(
    start_time: datetime, end_time: datetime, time_bucket: int
) -> int:
    """
    Returns the number of time buckets needed to go from `start_time` until
    `ned_time` in increments of `time_bucket` seconds.
    """
    # Divide total seconds by the bucket size, rounding up.
    return int(math.ceil((end_time - start_time).total_seconds() / time_bucket))


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


class QueryResult:
    """Utility for bucketing the results of a query."""

    def __init__(self, start_time: datetime, end_time: datetime, time_bucket: int):
        self._start_time = start_time
        self._end_time = end_time
        self._time_bucket = time_bucket
        self._buckets = []
        self._groups: Set[str] = set()

        # Initialize the buckets.
        curr_time = self._start_time
        for _ in range(calculate_num_buckets(start_time, end_time, time_bucket)):
            self._buckets.append(Bucket(curr_time))
            curr_time += timedelta(seconds=time_bucket)

    def increment(self, key: str, timestamp: datetime):
        """Increment the value of `key` at the specified `timestamp`."""
        if timestamp < self._start_time or timestamp > self._end_time:
            raise ValueError(f"Time out of bounds: {timestamp}.")
        # Calculate which bucket `timestamp` falls into.
        bucket_index = int(
            (timestamp - self._start_time).total_seconds() / self._time_bucket
        )
        self._buckets[bucket_index].data[key] += 1
        self._groups.add(key)

    def make_json(self) -> Dict:
        """
        Returns the data into the expected JSON result format.
        This causes a data copy so it is a bit expensive.
        """
        # TODO: this copies the data when serializing to JSON.
        #   Would be good to just "natively" have it in the JSON dict.
        return {
            "all_keys": list(self._groups),
            "buckets": [bucket.json() for bucket in self._buckets],
        }
