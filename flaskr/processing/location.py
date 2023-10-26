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

import requests


@dc.dataclass
class Location:
    country_name: str = None
    city: str = None
    region_name: str = None


# Used for accessing the `freegeoip` API
LOCATION_API_URL = "https://freegeoip.app/json/"
LOCATION_API_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
}


def lookup_location(ip_addr: str) -> Location:
    """Query the FreeGeoIP API."""
    response = requests.request(
        "GET",
        LOCATION_API_URL + ip_addr,
        headers=LOCATION_API_HEADERS,
    )
    if response.status_code == 200:
        return Location(
            country_name=response.json().get("country_name"),
            city=response.json().get("city"),
            region_name=response.json().get("region_name"),
        )
    else:
        raise ValueError(response.text)
