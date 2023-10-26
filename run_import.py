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
import requests

i = 0
with open("log2.txt") as f:
    for line in f:
        i += 1
        first_comma = line.index(",")
        second_comma = line.index(",", first_comma + 1)
        third_comma = line.index(",", second_comma + 1)
        timestamp = line[:first_comma]
        print(timestamp)
        url = line[first_comma + 1 : second_comma]
        ip = line[second_comma + 1 : third_comma]
        agent = line[third_comma + 1 :]

        res = requests.post(
            "http://127.0.0.1:5000/api/v1/traffic",
            json={
                "url": url,
                "ip_addr": ip,
                "user_agent": agent,
                "timestamp": timestamp,
            },
            headers={"Authorization": "x123456"},
        )
        print(res)
