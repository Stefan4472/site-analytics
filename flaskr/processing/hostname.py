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
import socket
from dataclasses import dataclass
from typing import Optional

from flask import current_app

# BOT_KEYWORDS = [
#     "bot",
#     "scan",
#     "surf",
#     "spider",
#     "crawl",
#     "pool",
#     "ip189",
#     "amazon",
#     "google",
#     "bezeqint",
#     "greenhousedata",
#     "comcastbusiness",
#     "dataprovider",
# ]


@dataclass
class HostnameInfo:
    hostname: str
    domain: str


def lookup_hostname(ip_address: str) -> Optional[HostnameInfo]:
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
    except (socket.herror, socket.gaierror):
        current_app.logger.warning("Socket error.")
        return None

    # For the rare case that 'hostname' = Nan
    if isinstance(hostname, float):
        current_app.logger.warning("hostname = Nan")
        return None

    segments = hostname.split(".")
    domain = segments[-2] + "." + segments[-1] if len(segments) > 1 else hostname
    return HostnameInfo(hostname, domain)


#
#
# def is_bot(hostname: str) -> bool:
#     # If the hostname couldn't be resolved, we can't assume it's a bot
#     if not hostname:
#         return False
#     return any(k in hostname.lower() for k in BOT_KEYWORDS)
