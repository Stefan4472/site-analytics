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
from flaskr.processing.ip_lookup import IpAddressInfo, lookup_ip_address


class ViewProcessor:
    """
    Processes RawViews, deriving information from the IP address and user agent.
    """

    def __init__(self):
        self._ip_cache = pylru.lrucache(512)
        # ip-api is limited to 45 requests per minute.
        self._lookup_throttler = ratelimiter.RateLimiter(45, 60)

    def process_view(self, raw_view: RawView) -> ProcessedView:
        user_agent = user_agents.parse(raw_view.user_agent)
        location = self._lookup_ip(raw_view.ip_address)
        is_bot = self._is_bot(user_agent)
        return ProcessedView(
            url=raw_view.url,
            ip_address=raw_view.ip_address,
            user_agent=raw_view.user_agent,
            timestamp=raw_view.timestamp,
            process_timestamp=datetime.now(),
            is_bot=is_bot,
            hostname=location.hostname if location else None,
            domain=location.domain if location else None,
            country=location.country if location else None,
            region=location.region if location else None,
            city=location.city if location else None,
            zip=location.zip if location else None,
            lat=location.lat if location else None,
            lon=location.lon if location else None,
            isp=location.isp if location else None,
            org=location.org if location else None,
            operating_system_family=user_agent.os.family,
            operating_system_version=user_agent.os.version_string,
            browser_family=user_agent.browser.family,
            browser_version=user_agent.browser.version_string,
            device_family=user_agent.device.family,
            device_brand=user_agent.device.brand,
            device_type=self._device_type(user_agent),
        )

    def _lookup_ip(self, ip_address: str) -> IpAddressInfo:
        """
        Returns location information for the specified IP address.

        Internally makes a request to an external API. Uses an LRU cache to
        reduce API calls and respects the location QPS limit.
        """
        lookup = self._ip_cache.get(ip_address, None)
        if lookup:
            return lookup
        with self._lookup_throttler:
            ip_info = lookup_ip_address(ip_address)
            self._ip_cache[ip_address] = ip_info
            return ip_info

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
