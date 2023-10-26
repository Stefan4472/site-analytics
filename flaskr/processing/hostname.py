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
import typing


# TODO: NARROW THE LIST? SEE HOW WELL THE "REQUESTS-PER-SECOND" METRIC WORKS
BOT_KEYWORDS = [
    'bot',
    'scan',
    'surf',
    'spider',
    'crawl',
    'pool',
    'ip189',
    'amazon',
    'google',
    'bezeqint',
    'greenhousedata',
    'comcastbusiness',
    'dataprovider',
]


def lookup_hostname(ip_address: str) -> str:
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
    except (socket.herror, socket.gaierror):
        raise ValueError('Socket error')

    # For the rare case that 'hostname' = Nan
    if isinstance(hostname, float):
        raise ValueError('hostname = Nan')

    return hostname


def domain_from_hostname(hostname) -> typing.Optional[str]:
    if not hostname or '.' not in hostname:
        return hostname
    segments = hostname.split('.')
    return segments[-2] + '.' + segments[-1]


def is_bot(hostname: str) -> bool:
    # If the hostname couldn't be resolved, we can't assume it's a bot
    if not hostname:
        return False
    return any(k in hostname.lower() for k in BOT_KEYWORDS)
