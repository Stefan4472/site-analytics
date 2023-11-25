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
from datetime import datetime
from typing import List, Set

import matplotlib.pyplot as plt
import requests


def get_groups(res: dict) -> Set[str]:
    groups: Set[str] = set()
    for bucket in res:
        for col in bucket["data"]:
            groups.add(col)
    return groups


if __name__ == "__main__":
    response = requests.get(
        r"http://127.0.0.1:5000/api/v1/data/query",
        headers={"Authorization": "1234"},
        params={
            "start_time": r"2020-04-01T20:00:00.000000",
            "end_time": r"2020-07-01T20:37:39.695580",
            "filter_by": "Humans",
            "group_by": "Country",
            "time_bucket": 86400,
        },
    )
    if response.status_code != 200:
        raise ValueError(f"Error: {response.status_code} {response.text}")
    # print(response.text)

    series = {group: [] for group in response.json()["all_keys"]}
    x_axis: List[datetime] = []
    for bucket in response.json()["buckets"]:
        x_axis.append(datetime.fromisoformat(bucket["timestamp"]))
        for group_name in series:
            series[group_name].append(bucket["data"].get(group_name, 0))
    # print(x_axis)
    # print(series)

    fig, ax = plt.subplots()
    fig.suptitle("Views per Week")
    ax.set_ylabel("Number of Views")
    for group_name in series:
        ax.plot(x_axis, series[group_name], label=group_name, linestyle="--")
    ax.grid(True)
    fig.legend()
    fig.savefig("plot.jpg")
    plt.show()
