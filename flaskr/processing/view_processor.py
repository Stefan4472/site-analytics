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

import pylru
import ratelimiter
import user_agents
from user_agents.parsers import UserAgent

from flaskr.models.processed_view import ProcessedView
from flaskr.models.raw_view import RawView
from flaskr.processing.hostname import HostnameInfo, lookup_hostname
from flaskr.processing.location import Location, lookup_location


class ViewProcessor:
    """
    Processes RawViews, deriving information from the IP address and user agent.
    """

    def __init__(self, max_location_qps: int = 1, max_hostname_qps: int = 1):
        self._location_cache = pylru.lrucache(512)
        self._hostname_cache = pylru.lrucache(512)
        self._location_throttler = ratelimiter.RateLimiter(max_location_qps)
        self._hostname_throttler = ratelimiter.RateLimiter(max_hostname_qps)

    def process_view(self, raw_view: RawView) -> ProcessedView:
        user_agent = user_agents.parse(raw_view.user_agent)
        location = self._get_location(raw_view.ip_address)
        is_bot = self._is_bot(user_agent)
        hostname = self._get_hostname(raw_view.ip_address) if is_bot else None
        return ProcessedView(
            url=raw_view.url,
            ip_address=raw_view.ip_address,
            user_agent=raw_view.user_agent,
            timestamp=raw_view.timestamp,
            process_timestamp=datetime.now(),
            is_bot=is_bot,
            hostname=hostname.hostname if hostname else None,
            domain=hostname.domain if hostname else None,
            city=location.city if location else None,
            region=location.region_name if location else None,
            country=location.country_name if location else None,
            operating_system_family=user_agent.os.family,
            operating_system_version=user_agent.os.version_string,
            browser_family=user_agent.browser.family,
            browser_version=user_agent.browser.version_string,
            device_family=user_agent.device.family,
            device_brand=user_agent.device.brand,
            device_type=self._device_type(user_agent),
        )

    def _get_location(self, ip_address: str) -> Location:
        """
        Returns location information for the specified IP address.

        Internally makes a request to an external API. Uses an LRU cache to
        reduce API calls and respects the location QPS limit.
        """
        lookup = self._location_cache.get(ip_address, None)
        if lookup:
            return lookup
        with self._location_throttler:
            location = lookup_location(ip_address)
            self._location_cache[ip_address] = location
            return location

    def _get_hostname(self, ip_address: str) -> HostnameInfo:
        """
        Returns hostname information for the specified IP address.

        Internally makes a request to an external API. Uses an LRU cache to
        reduce API calls and respects the location QPS limit.
        """
        lookup = self._hostname_cache.get(ip_address, None)
        if lookup:
            return lookup
        with self._hostname_throttler:
            hostname = lookup_hostname(ip_address)
            self._hostname_cache[ip_address] = hostname
            return hostname

    @staticmethod
    def _is_bot(user_agent: UserAgent) -> bool:
        """Returns whether the user agent is suspected to be from a bot."""
        return user_agent.is_bot

    @staticmethod
    def _device_type(user_agent: UserAgent) -> str:
        if user_agent.is_mobile:
            return "Mobile"
        elif user_agent.is_tablet:
            return "Tablet"
        elif user_agent.is_pc:
            return "PC"
        else:
            return "Unknown"
