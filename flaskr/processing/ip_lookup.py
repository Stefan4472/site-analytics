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
from typing import Optional

import requests


@dc.dataclass
class IpAddressInfo:
    """Stores data retrieved from the ip-api for a single IP address."""

    country: str = None
    region: str = None
    city: str = None
    zip: str = None
    lat: str = None
    lon: str = None
    isp: str = None
    org: str = None
    # Hostname derived via reverse DNS lookup.
    hostname: str = None
    # Domain extracted from the hostname.
    domain: str = None


def get_domain(hostname: str) -> Optional[str]:
    """Extracts the domain from a hostname."""
    hostname_segments = hostname.split(".")
    return (
        hostname_segments[-2] + "." + hostname_segments[-1]
        if len(hostname_segments) > 1
        else None
    )


def lookup_ip_address(ip_address: str) -> IpAddressInfo:
    """
    Queries the ip-api API and returns information received for the given IP address.

    It is the responsibility of the caller to ensure that rate limits are adhered to.
    Throws ValueError if the request fails.
    """
    # See https://ip-api.com/docs/api:json.
    response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=63225")
    response_json = response.json()
    if response.status_code != 200 or response_json["status"] != "success":
        raise ValueError(
            f'Request failed with status {response.status_code}: {response_json["message"]}'
        )
    return IpAddressInfo(
        country=response_json.get("country", None),
        region=response_json.get("regionName", None),
        city=response_json.get("city", None),
        zip=response_json.get("zip", None),
        lat=response_json.get("lat", None),
        lon=response_json.get("lon", None),
        isp=response_json.get("isp", None),
        org=response_json.get("org", None),
        hostname=response_json.get("reverse", None),
        domain=get_domain(response_json.get("reverse", "")),
    )
